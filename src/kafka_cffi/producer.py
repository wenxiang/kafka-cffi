from kafka_cffi.utils import headers_to_c
from .client import BaseKafkaClient
from ._rdkafka import lib, ffi
from .errors import KafkaException, \
    KafkaError
from .message import Message
from .utils import ensure_bytes


@ffi.def_extern()
def producer_delivery_cb(rk, rkmessage, opaque):
    if rkmessage._private:
        # This callback was set in produce() so it takes precedence
        producer, cb = ffi.from_handle(rkmessage._private)
        # clear references to prevent memory leak
        producer.callbacks.remove(rkmessage._private)
    elif opaque:
        # This callback was set in Producer config
        producer = ffi.from_handle(opaque)
        if producer.on_delivery:
            cb = producer.on_delivery
        else:
            return

    else:
        # no callbacks, just return
        return

    if rkmessage.err:
        cb(KafkaError(rkmessage.err), Message(rkmessage))
    else:
        if not producer.dr_only_error:
            cb(None, Message(rkmessage))


class Producer(BaseKafkaClient):
    MODE = lib.RD_KAFKA_PRODUCER

    def __init__(self, *args, **kwargs):
        self.topics = {}
        self.callbacks = set()
        self.on_delivery = None
        self.dr_only_error = False
        super(Producer, self).__init__(*args, **kwargs)

    def __len__(self):
        return lib.rd_kafka_outq_len(self.rk)

    def parse_conf(self):
        super(Producer, self).parse_conf()

        on_delivery = self.conf_dict.get("on_delivery")
        if on_delivery:
            if not callable(on_delivery):
                raise KafkaException(KafkaError._INVALID_ARG,
                                     "on_delivery requires a callable")

            self.on_delivery = on_delivery

        lib.rd_kafka_conf_set_dr_msg_cb(self.rd_conf, lib.producer_delivery_cb)

        dr_only_error = self.conf_dict.get("delivery.report.only.error", False)
        if type(dr_only_error) is not bool:
            raise KafkaException(KafkaError._INVALID_ARG,
                                 "delivery.report.only.error requires bool")
        self.dr_only_error = dr_only_error

    def get_topic(self, topic):
        rkt = self.topics.get(topic)
        if rkt is None:
            rkt = lib.rd_kafka_topic_new(self.rk, topic, ffi.NULL)
            if rkt:
                self.topics[topic] = rkt
            else:
                raise KafkaException(KafkaError._INVALID_ARG)
        return rkt

    def destroy_topic(self, topic):
        rkt = self.topics.pop(topic)
        lib.rd_kafka_topic_destroy(rkt)

    def produce(self, topic, value="", key="", partition=-1, on_delivery=None,
                timestamp=None, headers=None, callback=None):
        on_delivery = on_delivery or callback
        topic = ensure_bytes(topic)
        value = ensure_bytes(value)
        key = ensure_bytes(key)

        rkt = self.get_topic(topic)
        if on_delivery:
            cb = ffi.new_handle((self, on_delivery))
            self.callbacks.add(cb)
        else:
            cb = ffi.NULL

        hdrs = headers and headers_to_c(headers) or ffi.NULL

        err = lib.produce(
            self.rk, rkt, partition, value, len(value), key, len(key),
            timestamp or 0, hdrs, cb)

        if err:
            # self.destroy_topic(topic)
            if err == KafkaError._QUEUE_FULL:
                raise BufferError(KafkaError(err).str())
            else:
                raise KafkaException(err)

    def poll(self, timeout=0):
        timeout = int(timeout * 1000) if timeout >= 0 else -1
        return lib.rd_kafka_poll(self.rk, timeout)

    def flush(self, timeout=-1):
        timeout = int(timeout * 1000) if timeout >= 0 else -1
        lib.rd_kafka_flush(self.rk, timeout)
        return lib.rd_kafka_outq_len(self.rk)

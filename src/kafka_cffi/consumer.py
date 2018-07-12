from kafka_cffi.client import BaseKafkaClient
from kafka_cffi.errors import KafkaException, KafkaError
from ._rdkafka import lib, ffi


@ffi.def_extern()
def consumer_offset_commit_cb(rk, err, c_parts, opaque):
    # TODO
    pass


@ffi.def_extern()
def consumer_rebalance_cb(rk, err, c_parts, opaque):
    # TODO
    pass


class Consumer(BaseKafkaClient):
    MODE = lib.RD_KAFKA_CONSUMER

    def __init__(self, *args, **kwargs):
        self.on_commit = None
        super(Consumer, self).__init__(*args, **kwargs)

    def parse_conf(self):
        super(Consumer, self).parse_conf()

        on_commit = self.conf_dict.get("on_commit")
        if on_commit:
            if not callable(on_commit):
                raise KafkaException(KafkaError._INVALID_ARG,
                                     "on_commit requires a callable")
            self.on_commit = on_commit

            lib.rd_kafka_conf_set_offset_commit_cb(
                self.rd_conf, lib.consumer_offset_commit_cb)

        lib.rd_kafka_conf_set_rebalance_cb(
            self.rd_conf, lib.consumer_rebalance_cb)

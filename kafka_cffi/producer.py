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
		cb(KafkaError(rkmessage.err), None)
	else:
		cb(None, Message(rkmessage))


class Producer(BaseKafkaClient):

	MODE = lib.RD_KAFKA_PRODUCER

	def __init__(self, *args, **kwargs):
		self.topics = {}
		self.callbacks = set()
		self.on_delivery = None
		super(Producer, self).__init__(*args, **kwargs)

	def parse_conf(self):
		super(Producer, self).parse_conf()

		on_delivery = self.conf_dict.get("on_delivery")
		if on_delivery:
			if not callable(on_delivery):
				raise KafkaException(KafkaError._INVALID_ARG,
					"on_delivery requires a callable")

			self.on_delivery = on_delivery

		lib.rd_kafka_conf_set_dr_msg_cb(self.rd_conf, lib.producer_delivery_cb)

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
			timestamp=None):
		topic = ensure_bytes(topic)
		value = ensure_bytes(value)
		key = ensure_bytes(key)

		rkt = self.get_topic(topic)
		if on_delivery:
			cb = ffi.new_handle((self, on_delivery))
			self.callbacks.add(cb)
		else:
			cb = ffi.NULL

		result = lib.rd_kafka_produce(
			rkt, partition, lib.RD_KAFKA_MSG_F_COPY,
			value, len(value), key, len(key), cb)
		if result == -1:
			self.destroy_topic(topic)
			raise KafkaException(lib.rd_kafka_last_error())

	def poll(self, timeout=0):
		timeout = int(timeout * 1000) if timeout >= 0 else -1
		return lib.rd_kafka_poll(self.rk, timeout)

	def flush(self, timeout=-1):
		timeout = int(timeout * 1000) if timeout >= 0 else -1
		res = lib.rd_kafka_flush(self.rk, timeout)
		if res != KafkaError.NO_ERROR:
			raise KafkaException(res)

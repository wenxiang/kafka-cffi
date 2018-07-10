from kafka_cffi.config import Configuration
from ._rdkafka import lib, ffi
from .errors import KafkaException, \
	KafkaError
from .message import Message
from .utils import ensure_bytes, make_rd_conf, kafka_new


@ffi.def_extern()
def producer_delivery_cb(rk, rkmessage, opaque):
	if not (rkmessage._private or opaque):
		# no callbacks, return immediately
		return

	if rkmessage._private:
		tup = ffi.from_handle(rkmessage._private)
		producer, cb = tup
		# clear references to prevent memory leak
		producer.callbacks.remove(tup)

		if rkmessage.err:
			cb(KafkaError(rkmessage.err), None)
		else:
			cb(None, Message(rkmessage))

	elif opaque:
		producer = ffi.from_handle(opaque)



class Producer(object):

	def __init__(self, *args, **kwargs):
		self.config = Configuration(*args, **kwargs)
		self.topics = {}
		self.callbacks = set()

		lib.rd_kafka_conf_set_dr_msg_cb(self.config.rd_conf, lib.producer_delivery_cb)

		self.rk = kafka_new(lib.RD_KAFKA_PRODUCER, self.config.rd_conf)

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
			tup = (self, on_delivery)
			cb = ffi.new_handle(tup)
			self.callbacks.add(tup)
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

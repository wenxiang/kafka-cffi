from ._rdkafka import ffi, lib
from .errors import ConfigurationError, InitializationError
from .errors import KafkaException, KafkaError
from .message import Message

@ffi.def_extern("dr_msg_cb")
def dr_msg_cb(rk, rkmessage, opaque):
	cb_wrapper = ffi.from_handle(rkmessage._private)
	# clear references to prevent memory leak
	cb_wrapper.producer.callbacks.remove(rkmessage._private)
	cb_wrapper.producer = None

	if rkmessage.err:
		cb_wrapper.cb(KafkaError(rkmessage.err), None)
	else:
		m = Message(rkmessage)
		cb_wrapper.cb(None, m)

class CallbackWrapper(object):
	__slots__ = ('producer', 'cb')

	def __init__(self, producer, cb):
		self.producer = producer
		self.cb = cb

class Producer(object):

	def __init__(self, conf):
		self.topics = {}
		self.callbacks = set()

		rd_conf = lib.rd_kafka_conf_new()
		errstr = ffi.new("char[256]")
		for k, v in conf.items():
			res = lib.rd_kafka_conf_set(rd_conf, k, v, errstr, 256)
			if res != lib.RD_KAFKA_CONF_OK:
				raise ConfigurationError(ffi.string(errstr))

		lib.rd_kafka_conf_set_dr_msg_cb(rd_conf, lib.dr_msg_cb)

		self.rk = lib.rd_kafka_new(lib.RD_KAFKA_PRODUCER, rd_conf, errstr, 256)
		if not self.rk:
			raise InitializationError(ffi.string(errstr))


	def get_topic(self, topic):
		rkt = self.topics.get(topic)
		if rkt is None:
			rkt = lib.rd_kafka_topic_new(self.rk, topic, ffi.NULL)
			if rkt:
				self.topics[topic] = rkt
			else:
				raise KafkaException(KafkaError(lib.RD_KAFKA_RESP_ERR__INVALID_ARG))
		return rkt

	def destroy_topic(self, topic):
		rkt = self.topics.pop(topic)
		lib.rd_kafka_topic_destroy(rkt)

	def produce(self, topic, value="", key="", partition=-1, on_delivery=None,
			timestamp=None):
		rkt = lib.rd_kafka_topic_new(self.rk, topic, ffi.NULL)
		if on_delivery:
			cb = ffi.new_handle(CallbackWrapper(self, on_delivery))
			self.callbacks.add(cb)
		else:
			cb = ffi.NULL

		result = lib.rd_kafka_produce(
				rkt, partition, lib.RD_KAFKA_MSG_F_COPY,
				value, len(value), key, len(key), cb)
		if result == -1:
			self.destroy_topic(topic)
			raise KafkaException(KafkaError(lib.rd_kafka_last_error()))

	def poll(self, timeout=0):
		timeout = int(timeout * 1000) if timeout >= 0 else -1
		return lib.rd_kafka_poll(self.rk, timeout)



from ._rdkafka import lib, ffi
from .errors import KafkaException, \
	KafkaError
from .message import Message
from .utils import ensure_bytes, make_rd_conf, kafka_new


@ffi.def_extern()
def producer_delivery_cb(rk, rkmessage, opaque):
	if not rkmessage._private:
		# no callbacks, return immediately
		return

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

	def __init__(self, *args, **kwargs):
		self.topics = {}
		self.callbacks = set()

		rd_conf = make_rd_conf(*args, **kwargs)
		lib.rd_kafka_conf_set_dr_msg_cb(rd_conf, lib.producer_delivery_cb)
		self.rk = kafka_new(lib.RD_KAFKA_PRODUCER, rd_conf)

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
			cb = ffi.new_handle(CallbackWrapper(self, on_delivery))
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

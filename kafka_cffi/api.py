from kafka_cffi.errors import ConfigurationError, InitializationError
from ._rdkafka import ffi, lib

class Producer(object):

	def __init__(self, conf):
		rd_conf = lib.rd_kafka_conf_new()
		errstr = ffi.new("char[256]")
		for k, v in conf.items():
			res = lib.rd_kafka_conf_set(rd_conf, k, v, errstr, 256)
			if res != lib.RD_KAFKA_CONF_OK:
				raise ConfigurationError(ffi.string(errstr))

		self.rk = lib.rd_kafka_new(lib.RD_KAFKA_PRODUCER, rd_conf, errstr, 256)
		if not self.rk:
			raise InitializationError(ffi.string(errstr))


	def produce(self, topic, value="", key="", partition=-1, on_delivery=None,
			timestamp=None):
		rkt = lib.rd_kafka_topic_new(self.rk, topic, ffi.NULL)
		return rkt

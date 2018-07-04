from ._rdkafka import ffi, lib

class ConfigurationError(Exception):
	pass

class InitializationError(Exception):
	pass

class KafkaError(object):

	__slots__ = ('__resp_err_t',)

	def __init__(self, resp_err_t):
		self.__resp_err_t = resp_err_t

	def code(self):
		return self.__resp_err_t

	def name(self):
		return ffi.string(lib.rd_kafka_err2name(self.__resp_err_t))

	def str(self):
		return ffi.string(lib.rd_kafka_err2str(self.__resp_err_t))

class KafkaException(Exception):
	pass

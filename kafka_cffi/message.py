from ._rdkafka import lib, ffi
from .errors import KafkaError

class Message(object):

	__slots__ = (
		"__rkmessage",
	)

	def __init__(self, rkmessage):
		self.__rkmessage = rkmessage

	def payload(self):
		return ffi.string(
			ffi.cast("const char *", self.__rkmessage.payload),
			self.__rkmessage.len)

	def error(self):
		if self.__rkmessage.err:
			return KafkaError(self.__rkmessage.err)

	def key(self):
		return ffi.string(
			ffi.cast("const char *", self.__rkmessage.key),
			self.__rkmessage.key_len)

	def offset(self):
		return self.__rkmessage.offset

	def partition(self):
		return self.__rkmessage.partition

	def timestamp(self):
		tstype = ffi.new("rd_kafka_timestamp_type_t *")
		ts = lib.rd_kafka_message_timestamp(self.__rkmessage, tstype)
		return (tstype[0], ts)

	def headers(self):
		# TODO
		pass

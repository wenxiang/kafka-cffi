import six

from ._rdkafka import lib, ffi


def ensure_bytes(s):
	if isinstance(s, six.binary_type):
		return s
	elif isinstance(s, six.text_type):
		return s.encode("utf8")
	elif isinstance(s, (long, int, float)):
		return bytes(s)
	else:
		raise TypeError("argument must be a string / bytes")


def libversion():
	return lib.rd_kafka_version(), ffi.string(lib.rd_kafka_version_str())

def headers_to_c(headers):
	if type(headers) is not list:
		raise TypeError("Headers are expected to be a "
		                "list of (key, value) tuples")




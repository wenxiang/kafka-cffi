import six

from ._rdkafka import lib, ffi
from .errors import InitializationError


def ensure_bytes(s):
	if isinstance(s, six.binary_type):
		return s
	elif isinstance(s, six.text_type):
		return s.encode("utf8")
	else:
		raise TypeError("argument must be a string / bytes")


def kafka_new(_type, conf):
	errstr = ffi.new("char[256]")
	rk = lib.rd_kafka_new(_type, conf, errstr, 256)
	if not rk:
		lib.rd_kafka_conf_destroy(conf)
		raise InitializationError(ffi.string(errstr))
	return rk

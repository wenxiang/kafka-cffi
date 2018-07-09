import six

from kafka_cffi.errors import KafkaException, KafkaError
from .errors import ConfigurationError, InitializationError
from ._rdkafka import lib, ffi


def ensure_bytes(s):
	if isinstance(s, six.binary_type):
		return s
	elif isinstance(s, six.text_type):
		return s.encode("utf8")
	else:
		raise TypeError("argument must be a string / bytes")

error_callbacks = {}


@ffi.def_extern()
def error_cb (rk, err, reason, opaque):
	pass


def make_rd_conf(*args, **kwargs):
	confdict = {}
	if args:
		if len(args) > 1:
			raise TypeError("expected tuple containing single dict")
		if type(args[0]) is not dict:
			raise TypeError("expected configuration dict")
		confdict.update(args[0])

	if kwargs:
		confdict.update(kwargs)

	if len(confdict) == 0:
		raise TypeError("expected configuration dict")

	conf = lib.rd_kafka_conf_new()
	tconf = lib.rd_kafka_topic_conf_new()
	errstr = ffi.new("char[256]")

	# confluent_kafka settings:
	lib.rd_kafka_topic_conf_set(tconf, "produce.offset.report", "true",
		ffi.NULL, 0)

	# configure plugins first
	lib_path = confdict.pop("plugin.library.paths", None)
	if lib_path:
		if(lib.rd_kafka_conf_set(conf, b"plugin.library.paths",
				ensure_bytes(lib_path), errstr, 256) != 0):
			raise KafkaException(KafkaError._INVALID_ARG)

	for k, v in confdict.items():

		res = lib.rd_kafka_conf_set(conf,
			ensure_bytes(k), ensure_bytes(v), errstr, 256)
		if res != 0:
			lib.rd_kafka_conf_destroy(conf)
			lib.rd_kafka_topic_conf_destroy(tconf)
			raise ConfigurationError(ffi.string(errstr))

	lib.rd_kafka_conf_set_default_topic_conf(conf, tconf)
	return conf


def kafka_new(_type, conf):
	errstr = ffi.new("char[256]")
	rk = lib.rd_kafka_new(_type, conf, errstr, 256)
	if not rk:
		lib.rd_kafka_conf_destroy(conf)
		raise InitializationError(ffi.string(errstr))
	return rk



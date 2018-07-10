import logging

from ._rdkafka import lib, ffi
from .errors import KafkaError, KafkaException
from .utils import ensure_bytes

LOGLEVEL_MAP = [
	50, # 0 = LOG_EMERG   -> logging.CRITICAL
	50, # 1 = LOG_ALERT   -> logging.CRITICAL
	50, # 2 = LOG_CRIT    -> logging.CRITICAL
	40, # 3 = LOG_ERR     -> logging.ERROR
	30, # 4 = LOG_WARNING -> logging.WARNING
	20, # 5 = LOG_NOTICE  -> logging.INFO
	20, # 6 = LOG_INFO    -> logging.INFO
	10, # 7 = LOG_DEBUG   -> logging.DEBUG
]


@ffi.def_extern()
def error_cb(rk, err, reason, opaque):
	if opaque:
		config = ffi.from_handle(opaque)
		if config.error_cb:
			config.error_cb(KafkaError(err), ffi.string(reason))


@ffi.def_extern()
def stats_cb(rk, json, json_len, opaque):
	if opaque:
		config = ffi.from_handle(opaque)
		if config.stats_cb:
			json_str = ffi.string(json, json_len)
			config.stats_cb(json_str)

	return 0


@ffi.def_extern()
def throttle_cb(rk, broker_name, broker_id, throttle_time_ms, opaque):
	if opaque:
		config = ffi.from_handle(opaque)
		if config.throttle_cb:
			config.throttle_cb(ffi.string(broker_name), broker_id, throttle_time_ms)


@ffi.def_extern()
def log_cb(rk, level, fac, buf, opaque):
	if opaque:
		config = ffi.from_handle(opaque)
		if config.logger:
			config.logger.log(LOGLEVEL_MAP[level], "%s [%s] %s",
				ffi.string(fac), ffi.string(lib.rd_kafka_name(rk)), ffi.string(buf))


class Configuration(object):
	_default_conf = {
		"produce.offset.report": "true",
	}

	__slots__ = (
		"conf_dict", "stats_cb", "error_cb", "throttle_cb",
		"rd_conf", "rd_topic_conf", "logger",
	)

	def __init__(self, *args, **kwargs):
		self.conf_dict = self.make_conf_dict(*args, **kwargs)
		self.stats_cb = None
		self.error_cb = None
		self.throttle_cb = None
		self.logger = None

		self.rd_conf = lib.rd_kafka_conf_new()
		self.rd_topic_conf = None

		try:
			self.parse_conf()
		except:
			self.destroy()
			raise

	def destroy(self):
		lib.rd_kafka_conf_destroy(self.rd_conf)
		self.rd_conf = None
		if self.rd_topic_conf:
			lib.rd_kafka_topic_conf_destroy(self.rd_topic_conf)
			self.rd_topic_conf = None

	@classmethod
	def make_conf_dict(cls, *args, **kwargs):
		conf_dict = dict(cls._default_conf)
		if args:
			if len(args) > 1:
				raise TypeError("expected tuple containing single dict")
			if type(args[0]) is not dict:
				raise TypeError("expected configuration dict")
			conf_dict.update(args[0])

		if kwargs:
			conf_dict.update(kwargs)

		if len(conf_dict) == 0:
			raise TypeError("expected configuration dict")

		return conf_dict

	def parse_conf(self):
		lib_path = self.conf_dict.pop("plugin.library.paths", None)
		rd_topic_conf = None
		if lib_path:
			# configure plugins first
			self.populate_conf("plugin.library.paths", lib_path)

		for k, v in self.conf_dict.items():

			if k == "default.topic.config":
				self.populate_topic_conf(k, v)
				lib.rd_kafka_conf_set_default_topic_conf(rd_topic_conf)

			elif k == "error_cb":
				if not callable(v):
					raise TypeError("expected error_cb property as a callable function")
				self.error_cb = v
				lib.rd_kafka_conf_set_error_cb(self.rd_conf, lib.error_cb)

			elif k == "throttle_cb":
				if not callable(v):
					raise TypeError(
						"expected throttle_cb property as a callable function")
				self.throttle_cb = v
				lib.rd_kafka_conf_set_throttle_cb(self.rd_conf, lib.throttle_cb)

			elif k == "stats_cb":
				if not callable(v):
					raise TypeError("expected stats_cb property as a callable function")
				self.stats_cb = v
				lib.rd_kafka_conf_set_stats_cb(self.rd_conf, lib.stats_cb)

			elif k == "logger":
				if not isinstance(v, logging.Handler):
					raise TypeError("expected logger as an instance of logging.Handler")
				self.logger = v
				lib.rd_kafka_conf_set_log_cb(self.rd_conf, lib.log_cb)
				self.populate_conf("log.queue", "true")

			elif k in ("on_delivery", "delivery")

			else:
				self.populate_conf(k, v)

		if self.stats_cb or self.throttle_cb or self.error_cb or self.logger:
			handle = ffi.new_handle(self)
			lib.rd_kafka_conf_set_opaque(self.rd_conf, handle)
			if rd_topic_conf:
				lib.rd_kafka_topic_conf_set_opaque(rd_topic_conf, handle)

	def populate_topic_conf(self, what, conf):
		if type(conf) is not dict:
			raise KafkaException(KafkaError._INVALID_ARG,
				"%s: requires a dict" % what)

		self.rd_topic_conf = lib.rd_kafka_topic_conf_new()
		errstr = ffi.new("char[256]")
		for k, v in conf.items():
			if (lib.rd_kafka_topic_conf_set(self.rd_topic_conf,
					ensure_bytes(k), ensure_bytes(v), errstr, 256) != 0):
				raise KafkaException(KafkaError._INVALID_ARG, "%s: %s" % (k, errstr))

	def populate_conf(self, k, v):
		errstr = ffi.new("char[256]")
		if (lib.rd_kafka_conf_set(self.rd_conf, ensure_bytes(k),
				ensure_bytes(v), errstr, 256) != 0):
			raise KafkaException(KafkaError._INVALID_ARG, "%s: %s" % (k, errstr))

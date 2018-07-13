import logging

from ._rdkafka import lib, ffi
from .errors import KafkaException, KafkaError
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


class BaseKafkaClient(object):
    _default_conf = {
        "produce.offset.report": "true",
    }

    MODE = None

    def __init__(self, *args, **kwargs):
        self.conf_dict = self.parse_args(*args, **kwargs)
        self.stats_cb = None
        self.error_cb = None
        self.throttle_cb = None
        self.logger = None

        self.rk = None
        self.rd_conf = lib.rd_kafka_conf_new()
        self.rd_topic_conf = None
        self.handle = ffi.new_handle(self)

        try:
            self.parse_conf()
            errstr = ffi.new("char[256]")
            self.rk = lib.rd_kafka_new(self.MODE, self.rd_conf, errstr, 256)
            if not self.rk:
                raise KafkaException(
                    lib.rd_kafka_last_error(),
                    "Failed to create client: %s" % ffi.string(errstr))

        except Exception:
            self.destroy()
            raise

    def destroy(self):
        self.handle = None
        if self.rd_conf:
            lib.rd_kafka_conf_destroy(self.rd_conf)
            self.rd_conf = None
        if self.rd_topic_conf:
            lib.rd_kafka_topic_conf_destroy(self.rd_topic_conf)
            self.rd_topic_conf = None
        if self.rk:
            lib.rd_kafka_destroy(self.rk)
            self.rk = None

    def parse_args(self, *args, **kwargs):
        conf_dict = dict(self._default_conf)
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

    def populate_rd_topic_conf(self, what, conf):
        if type(conf) is not dict:
            raise KafkaException(KafkaError._INVALID_ARG,
                                 "%s: requires a dict" % what)

        self.rd_topic_conf = lib.rd_kafka_topic_conf_new()
        errstr = ffi.new("char[256]")
        for k, v in conf.items():
            if (lib.rd_kafka_topic_conf_set(self.rd_topic_conf,
                                            ensure_bytes(k), ensure_bytes(v),
                                            errstr, 256) != 0):
                raise KafkaException(KafkaError._INVALID_ARG,
                                     "%s: %s" % (k, ffi.string(errstr)))

    def populate_rd_conf(self, k, v):
        errstr = ffi.new("char[256]")
        if (lib.rd_kafka_conf_set(self.rd_conf, ensure_bytes(k),
                                  ensure_bytes(v), errstr, 256) != 0):
            raise KafkaException(KafkaError._INVALID_ARG,
                                 "%s: %s" % (k, ffi.string(errstr)))

    def parse_conf(self):
        lib_path = self.conf_dict.pop("plugin.library.paths", None)
        if lib_path:
            # configure plugins first
            self.populate_rd_conf("plugin.library.paths", lib_path)

        for k, v in self.conf_dict.items():

            if k == "default.topic.config":
                self.populate_rd_topic_conf(k, v)
                lib.rd_kafka_topic_conf_set_opaque(self.rd_topic_conf,
                                                   self.handle)
                lib.rd_kafka_conf_set_default_topic_conf(
                    self.rd_conf, self.rd_topic_conf)

            elif k == "error_cb":
                if not callable(v):
                    raise TypeError(
                        "expected error_cb property as a callable function")
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
                    raise TypeError(
                        "expected stats_cb property as a callable function")
                self.stats_cb = v
                lib.rd_kafka_conf_set_stats_cb(self.rd_conf, lib.stats_cb)

            elif k == "logger":
                if not isinstance(v, logging.Handler):
                    raise TypeError(
                        "expected logger as an instance of logging.Handler")
                self.logger = v
                lib.rd_kafka_conf_set_log_cb(self.rd_conf, lib.log_cb)
                self.populate_rd_conf("log.queue", "true")

            elif k in ("on_delivery", "delivery.report.only.error",
                       "on_commit"):
                # producer & consumer specific - to be handled in subclass
                pass

            else:
                self.populate_rd_conf(k, v)

        lib.rd_kafka_conf_set_opaque(self.rd_conf, self.handle)

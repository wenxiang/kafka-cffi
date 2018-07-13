import logging

from ._rdkafka import lib, ffi
from .errors import KafkaException, KafkaError
from .utils import ensure_bytes


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

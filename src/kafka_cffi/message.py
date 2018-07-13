from ._rdkafka import lib, ffi
from .errors import KafkaError


class Message(object):
    __slots__ = (
        "__payload",
        "__key",
        "__partition",
        "__offset",
        "__timestamp",
        "__error",
        "__topic"
    )

    def __init__(self, rkmessage):
        self.__topic = ffi.string(lib.rd_kafka_topic_name(rkmessage.rkt))
        self.__payload = ffi.string(
            ffi.cast("const char *", rkmessage.payload), rkmessage.len)
        self.__key = ffi.string(
            ffi.cast("const char *", rkmessage.key), rkmessage.key_len)
        self.__partition = rkmessage.partition
        self.__offset = rkmessage.offset
        tstype = ffi.new("rd_kafka_timestamp_type_t *")
        ts = lib.rd_kafka_message_timestamp(rkmessage, tstype)
        self.__timestamp = (tstype[0], ts)
        if rkmessage.err:
            self.__error = KafkaError(rkmessage.err)

    def __len__(self):
        return self.__payload and len(self.__payload) or 0

    def topic(self):
        return self.__topic

    def payload(self):
        return self.__payload

    def value(self):
        return self.__payload

    def error(self):
        return self.__error

    def key(self):
        return self.__key

    def offset(self):
        return self.__offset

    def partition(self):
        return self.__partition

    def timestamp(self):
        return self.__timestamp

    def headers(self):
        # TODO
        raise NotImplementedError

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
        "__topic",
        "__headers"
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

        c_header_pt = ffi.new("rd_kafka_headers_t **")
        lib.rd_kafka_message_headers(rkmessage, c_header_pt)
        c_header = c_header_pt[0]

        hdcount = 0
        if c_header != ffi.NULL:
            hdcount = lib.rd_kafka_header_cnt(c_header)

        c_hd_key = ffi.new("const char **")
        c_hd_payload = ffi.new("const char **")
        c_hd_size = ffi.new("size_t *")
        self.__headers = []
        for idx in range(hdcount):
            error = lib.rd_kafka_header_get_all(
                c_header, idx, c_hd_key, ffi.cast("const void **", c_hd_payload), c_hd_size)
            if error == 0:
                self.__headers.append(
                    (ffi.string(c_hd_key[0]),
                     ffi.unpack(c_hd_payload[0], int(c_hd_size[0])))
                )

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
        return self.__headers

import six

from ._rdkafka import lib, ffi
from .errors import KafkaException


def ensure_bytes(s):
    if isinstance(s, six.binary_type):
        return s
    elif isinstance(s, six.text_type):
        return s.encode("utf8")
    elif isinstance(s, six.integer_types + (float,)):
        return str(s).encode("utf8")
    else:
        raise TypeError("argument must be a string / bytes")


def libversion():
    return ffi.string(lib.rd_kafka_version_str()), lib.rd_kafka_version()


def version():
    return "0.11.4", 0x000b0400


HEADER_TYPE_ERR = "Headers are expected to be a list of (key,value) tuples"


def headers_to_c(headers):
    if type(headers) is not list:
        raise TypeError(HEADER_TYPE_ERR)

    rd_headers = lib.rd_kafka_headers_new(len(headers))
    for tup in headers:
        try:
            if type(tup) is not tuple or len(tup) != 2:
                raise TypeError(HEADER_TYPE_ERR)

            key, value = tup
            key_b = ensure_bytes(key)
            if value is None:
                value_b = ffi.NULL
                value_len = 0
            else:
                value_b = ensure_bytes(value)
                value_len = len(value_b)

            err = lib.rd_kafka_header_add(
                rd_headers, key_b, len(key_b), value_b, value_len)

            if err:
                raise KafkaException(err, "Unable to create message headers")
        except Exception:
            lib.rd_kafka_headers_destroy(rd_headers)
            raise

    return rd_headers

from cffi import FFI

ffi = FFI()

KAFKA_CFFI_H = open("kafka_cffi.h", "r").read()
ffi.cdef(KAFKA_CFFI_H)

ffi.set_source("kafka_cffi._rdkafka", """
#include <librdkafka/rdkafka.h>
""", libraries=["rdkafka"])

if __name__ == "__main__":
	ffi.compile(verbose=True)

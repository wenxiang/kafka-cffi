from cffi import FFI

ffi = FFI()

ffi.cdef(open("src/_rdkafka.h", "r").read())

ffi.set_source("kafka_cffi._rdkafka", open("src/_rdkafka.c", "r").read(),
    libraries=["rdkafka"])

if __name__ == "__main__":
    ffi.compile(verbose=True)

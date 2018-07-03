from cffi import FFI

ffi = FFI()

ffi.cdef("""
typedef struct rd_kafka_s rd_kafka_t;
typedef struct rd_kafka_topic_s rd_kafka_topic_t;
typedef struct rd_kafka_conf_s rd_kafka_conf_t;
typedef struct rd_kafka_topic_conf_s rd_kafka_topic_conf_t;
typedef struct rd_kafka_queue_s rd_kafka_queue_t;
typedef struct rd_kafka_op_s rd_kafka_event_t;
typedef struct rd_kafka_topic_result_s rd_kafka_topic_result_t;

typedef enum rd_kafka_type_t {
	RD_KAFKA_PRODUCER,
	RD_KAFKA_CONSUMER
} rd_kafka_type_t;

rd_kafka_conf_t *rd_kafka_conf_new(void);

typedef enum {
	RD_KAFKA_CONF_OK = 0,
	...
} rd_kafka_conf_res_t;

rd_kafka_conf_res_t rd_kafka_conf_set(rd_kafka_conf_t *conf, 
	const char *name, 
	const char *value, 
	char *errstr, 
	size_t errstr_size);
	

rd_kafka_t *rd_kafka_new(rd_kafka_type_t type, 
	rd_kafka_conf_t *conf, 
	char *errstr, 
	size_t errstr_size);
	
	
rd_kafka_topic_t *rd_kafka_topic_new(rd_kafka_t *rk, const char *topic, 
	rd_kafka_topic_conf_t *conf);
""")

ffi.set_source("kafka_cffi._rdkafka", """
#include <librdkafka/rdkafka.h>
""", libraries=["rdkafka"])

if __name__ == "__main__":
	ffi.compile(verbose=True)

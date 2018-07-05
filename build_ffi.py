from cffi import FFI

ffi = FFI()

ffi.cdef("""
#define RD_KAFKA_MSG_F_COPY  0x2

typedef struct rd_kafka_s rd_kafka_t;
typedef struct rd_kafka_topic_s rd_kafka_topic_t;
typedef struct rd_kafka_conf_s rd_kafka_conf_t;
typedef struct rd_kafka_topic_conf_s rd_kafka_topic_conf_t;
typedef struct rd_kafka_queue_s rd_kafka_queue_t;
typedef struct rd_kafka_op_s rd_kafka_event_t;
typedef struct rd_kafka_topic_result_s rd_kafka_topic_result_t;
typedef struct rd_kafka_headers_s rd_kafka_headers_t;

typedef enum rd_kafka_type_t {
	RD_KAFKA_PRODUCER,
	RD_KAFKA_CONSUMER
} rd_kafka_type_t;

typedef enum rd_kafka_timestamp_type_t {
...
} rd_kafka_timestamp_type_t;

typedef enum {
	...
} rd_kafka_resp_err_t;

typedef struct rd_kafka_message_s {
	rd_kafka_resp_err_t err;
	rd_kafka_topic_t *rkt;
	int32_t partition;
	void   *payload;
	size_t  len;
	void   *key;
	size_t  key_len;
	int64_t offset;
	void  *_private;
} rd_kafka_message_t;

typedef enum {
	...
} rd_kafka_conf_res_t;

rd_kafka_resp_err_t rd_kafka_last_error (void);
const char *rd_kafka_err2str (rd_kafka_resp_err_t err);
const char *rd_kafka_err2name (rd_kafka_resp_err_t err);
rd_kafka_conf_t *rd_kafka_conf_new(void);
rd_kafka_conf_res_t rd_kafka_conf_set(rd_kafka_conf_t *conf, const char *name, const char *value, char *errstr, size_t errstr_size);
extern "Python" static void dr_msg_cb(rd_kafka_t *rk, const rd_kafka_message_t *rkmessage, void *opaque);
void rd_kafka_conf_set_dr_msg_cb(rd_kafka_conf_t *conf, void (*dr_msg_cb) (rd_kafka_t *rk, const rd_kafka_message_t * rkmessage, void *opaque));
rd_kafka_t *rd_kafka_new(rd_kafka_type_t type, rd_kafka_conf_t *conf, char *errstr, size_t errstr_size);
rd_kafka_topic_t *rd_kafka_topic_new(rd_kafka_t *rk, const char *topic, rd_kafka_topic_conf_t *conf);
void rd_kafka_topic_destroy(rd_kafka_topic_t *rkt);
int rd_kafka_produce(rd_kafka_topic_t *rkt, int32_t partition, int msgflags, void *payload, size_t len, const void *key, size_t keylen, void *msg_opaque);
int rd_kafka_poll(rd_kafka_t *rk, int timeout_ms);
rd_kafka_resp_err_t rd_kafka_message_headers (const rd_kafka_message_t *rkmessage, rd_kafka_headers_t **hdrsp);
rd_kafka_resp_err_t rd_kafka_header_get_all (const rd_kafka_headers_t *hdrs, size_t idx, const char **namep, const void **valuep, size_t *sizep);
int64_t rd_kafka_message_timestamp (const rd_kafka_message_t *rkmessage, rd_kafka_timestamp_type_t *tstype);
rd_kafka_resp_err_t rd_kafka_flush (rd_kafka_t *rk, int timeout_ms);
""")

ffi.set_source("kafka_cffi._rdkafka", """
#include <librdkafka/rdkafka.h>
""", libraries=["rdkafka"])

if __name__ == "__main__":
	ffi.compile(verbose=True)

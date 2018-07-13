#define RD_KAFKA_MSG_F_COPY 0x2

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

typedef enum rd_kafka_timestamp_type_t {... } rd_kafka_timestamp_type_t;

typedef enum {... } rd_kafka_resp_err_t;

typedef struct rd_kafka_message_s {
  rd_kafka_resp_err_t err;
  rd_kafka_topic_t *rkt;
  int32_t partition;
  void *payload;
  size_t len;
  void *key;
  size_t key_len;
  int64_t offset;
  void *_private;
} rd_kafka_message_t;

typedef struct rd_kafka_topic_partition_s {
  char *topic;
  int32_t partition;
  int64_t offset;
  void *metadata;
  size_t metadata_size;
  void *opaque;
  rd_kafka_resp_err_t err;
  void *_private;
} rd_kafka_topic_partition_t;

typedef struct rd_kafka_topic_partition_list_s {
  int cnt;
  int size;
  rd_kafka_topic_partition_t *elems;
} rd_kafka_topic_partition_list_t;

int rd_kafka_version(void);

const char *rd_kafka_version_str (void);

typedef enum {... } rd_kafka_conf_res_t;

rd_kafka_resp_err_t rd_kafka_last_error(void);

const char *rd_kafka_err2str(rd_kafka_resp_err_t err);

const char *rd_kafka_err2name(rd_kafka_resp_err_t err);

rd_kafka_conf_t *rd_kafka_conf_new(void);

rd_kafka_conf_res_t rd_kafka_conf_set(rd_kafka_conf_t *conf, const char *name,
                                      const char *value, char *errstr,
                                      size_t errstr_size);

void rd_kafka_conf_set_dr_msg_cb(
    rd_kafka_conf_t *conf,
    void (*dr_msg_cb)(rd_kafka_t *rk, const rd_kafka_message_t *rkmessage,
                      void *opaque));

rd_kafka_t *rd_kafka_new(rd_kafka_type_t type, rd_kafka_conf_t *conf,
                         char *errstr, size_t errstr_size);

const char *rd_kafka_name(const rd_kafka_t *rk);

rd_kafka_topic_t *rd_kafka_topic_new(rd_kafka_t *rk, const char *topic,
                                     rd_kafka_topic_conf_t *conf);

const char *rd_kafka_topic_name(const rd_kafka_topic_t *rkt);

void rd_kafka_topic_destroy(rd_kafka_topic_t *rkt);

int rd_kafka_produce(rd_kafka_topic_t *rkt, int32_t partition, int msgflags,
                     void *payload, size_t len, const void *key, size_t keylen,
                     void *msg_opaque);

int rd_kafka_poll(rd_kafka_t *rk, int timeout_ms);

rd_kafka_headers_t *rd_kafka_headers_new (size_t initial_count);

void rd_kafka_headers_destroy (rd_kafka_headers_t *hdrs);

rd_kafka_resp_err_t rd_kafka_header_add (rd_kafka_headers_t *hdrs,
                     const char *name, ssize_t name_size,
                     const void *value, ssize_t value_size);

rd_kafka_resp_err_t
rd_kafka_message_headers(const rd_kafka_message_t *rkmessage,
                         rd_kafka_headers_t **hdrsp);

rd_kafka_resp_err_t rd_kafka_header_get_all(const rd_kafka_headers_t *hdrs,
                                            size_t idx, const char **namep,
                                            const void **valuep, size_t *sizep);

void rd_kafka_destroy(rd_kafka_t *rk);

void rd_kafka_conf_destroy(rd_kafka_conf_t *conf);

void rd_kafka_message_destroy(rd_kafka_message_t *rkmessage);

int64_t rd_kafka_message_timestamp(const rd_kafka_message_t *rkmessage,
                                   rd_kafka_timestamp_type_t *tstype);

rd_kafka_resp_err_t rd_kafka_flush(rd_kafka_t *rk, int timeout_ms);

void rd_kafka_conf_set_offset_commit_cb(
    rd_kafka_conf_t *conf,
    void (*offset_commit_cb)(rd_kafka_t *rk, rd_kafka_resp_err_t err,
                             rd_kafka_topic_partition_list_t *offsets,
                             void *opaque));

void rd_kafka_conf_set_rebalance_cb(
    rd_kafka_conf_t *conf,
    void (*rebalance_cb)(rd_kafka_t *rk, rd_kafka_resp_err_t err,
                         rd_kafka_topic_partition_list_t *partitions,
                         void *opaque));

void rd_kafka_topic_conf_destroy(rd_kafka_topic_conf_t *topic_conf);

rd_kafka_resp_err_t rd_kafka_poll_set_consumer(rd_kafka_t *rk);

rd_kafka_queue_t *rd_kafka_queue_get_consumer(rd_kafka_t *rk);

rd_kafka_topic_conf_t *rd_kafka_topic_conf_new(void);

rd_kafka_conf_res_t rd_kafka_topic_conf_set(rd_kafka_topic_conf_t *conf,
                         const char *name,
                         const char *value,
                         char *errstr, size_t errstr_size);

void rd_kafka_conf_set_default_topic_conf (rd_kafka_conf_t *conf,
                                           rd_kafka_topic_conf_t *tconf);

void rd_kafka_conf_set_error_cb(rd_kafka_conf_t *conf,
                 void  (*error_cb) (rd_kafka_t *rk, int err,
                            const char *reason,
                            void *opaque));

void rd_kafka_conf_set_stats_cb(rd_kafka_conf_t *conf,
                 int (*stats_cb) (rd_kafka_t *rk,
                          char *json,
                          size_t json_len,
                          void *opaque));

void rd_kafka_conf_set_throttle_cb (rd_kafka_conf_t *conf,
                    void (*throttle_cb) (
                        rd_kafka_t *rk,
                        const char *broker_name,
                        int32_t broker_id,
                        int throttle_time_ms,
                        void *opaque));

void rd_kafka_conf_set_log_cb(rd_kafka_conf_t *conf,
              void (*log_cb) (const rd_kafka_t *rk, int level,
                const char *fac, const char *buf));

void rd_kafka_conf_set_opaque(rd_kafka_conf_t *conf, void *opaque);

void rd_kafka_topic_conf_set_opaque(rd_kafka_topic_conf_t *conf, void *opaque);

int rd_kafka_outq_len(rd_kafka_t *rk);

rd_kafka_resp_err_t produce(
    rd_kafka_t *rk,
    rd_kafka_topic_t * rkt,
    int32_t partition,
    void *value, size_t value_len,
    void *key,   size_t key_len,
    int64_t timestamp,
    rd_kafka_headers_t *headers,
    void *opaque);

extern "Python"
static void producer_delivery_cb(rd_kafka_t *rk,
    const rd_kafka_message_t *rkmessage, void *opaque);

extern "Python"
static void consumer_offset_commit_cb(rd_kafka_t *rk, rd_kafka_resp_err_t err,
                          rd_kafka_topic_partition_list_t *c_parts,
                          void *opaque);

extern "Python"
static void consumer_rebalance_cb(rd_kafka_t *rk, rd_kafka_resp_err_t err,
                      rd_kafka_topic_partition_list_t *c_parts, void *opaque);

extern "Python"
static void error_cb(rd_kafka_t *rk, int err, const char *reason, void *opaque);

extern "Python"
static int stats_cb (rd_kafka_t *rk, char *json, size_t json_len, void *opaque);

extern "Python"
static void throttle_cb (rd_kafka_t *rk, const char *broker_name, int32_t broker_id,
    int throttle_time_ms, void *opaque);

extern "Python"
static void log_cb (const rd_kafka_t *rk, int level,
                const char *fac, const char *buf);

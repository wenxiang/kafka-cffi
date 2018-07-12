#include <librdkafka/rdkafka.h>

rd_kafka_resp_err_t produce(
    rd_kafka_t *rk,
    rd_kafka_topic_t * rkt,
    int32_t partition,
    void *value, size_t value_len,
    void *key,   size_t key_len,
    int64_t timestamp,
    rd_kafka_headers_t *headers,
    void *opaque)
{
    rd_kafka_resp_err_t err = RD_KAFKA_RESP_ERR_NO_ERROR;

    if (timestamp == 0 && headers == 0) {
        if (rd_kafka_produce(rkt, partition, RD_KAFKA_MSG_F_COPY,
                value, value_len, key, key_len, opaque) == -1)
            err = rd_kafka_last_error();
    } else {
        err = rd_kafka_producev(rk,
            RD_KAFKA_V_MSGFLAGS(RD_KAFKA_MSG_F_COPY),
            RD_KAFKA_V_RKT(rkt),
            RD_KAFKA_V_PARTITION(partition),
            RD_KAFKA_V_KEY(key, key_len),
            RD_KAFKA_V_VALUE(value, value_len),
            RD_KAFKA_V_TIMESTAMP(timestamp),
            RD_KAFKA_V_HEADERS(headers),
            RD_KAFKA_V_OPAQUE(opaque),
            RD_KAFKA_V_END
        );
    }

    return err;
}

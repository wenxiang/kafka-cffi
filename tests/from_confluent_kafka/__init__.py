import kafka_cffi
import sys

if "confluent_kafka" not in sys.modules:
    sys.modules["confluent_kafka"] = kafka_cffi
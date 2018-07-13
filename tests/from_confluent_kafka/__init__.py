import kafka_cffi
import sys
sys.modules["confluent_kafka"] = kafka_cffi

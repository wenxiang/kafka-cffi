CFFI based Python client for Apache Kafka
=========================================

**kafka-cffi** is a CFFI wrapper around [librdkafka](https://github.com/edenhill/librdkafka)

Features:

- API compatiblity with [confluent-kafka](https://github.com/confluentinc/confluent-kafka-python)
  allows it to be used as a drop in replacement
- Significantly better performance when used in PyPy (benchmarks below)
- Tested against confluent-kafka's test suite

Progress:

- [x] Producer
- [ ] Consumer
- [ ] AvroProducer
- [ ] AvroConsumer

Usage
=====

*Usage examples wholesale copied from confluent-kafka*

**Producer:**

```python
from kafka_cffi import Producer


p = Producer({'bootstrap.servers': 'mybroker1,mybroker2'})

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

for data in some_data_source:
    # Trigger any available delivery report callbacks from previous produce() calls
    p.poll(0)

    # Asynchronously produce a message, the delivery report callback
    # will be triggered from poll() above, or flush() below, when the message has
    # been successfully delivered or failed permanently.
    p.produce('mytopic', data.encode('utf-8'), callback=delivery_report)

# Wait for any outstanding messages to be delivered and delivery report
# callbacks to be triggered.
p.flush()
```

Install
=======

Prerequisites:
- CPython / PyPy 2.7x & 3.x
- librdkafka >= v0.11.4

Tests
=====

For now only we are only passing `Producer` and `integration_test.py --producer`
tests. The goal is to pass all of confluent-kafka's tests.


Performance
===========

The `benchmarks` directory contains the jupyter notebooks used for benchmarks.
Here are the results we have gathered so far on a core i7 2.6GHz Macbook Pro 13.
On PyPy, kafka-cffi Producers are 4-5x faster than confluent-kafka. 

Producer
--------

| Client | Platform | Message Size | DR Callbacks | msgs / s  |
| - | - | - | - | - |
| confluent-kafka | CPython 2.7 | 100 | n | 415,044 |
| confluent-kafka | CPython 2.7 | 450 | n | 205,385 |
| confluent-kafka | CPython 2.7 | 450 | y | 230,279 |
| kafka-cffi | CPython 2.7 | 100 | n | 297,487 |
| kafka-cffi | CPython 2.7 | 450| n | 153,077 |
| kafka-cffi | CPython 2.7 | 450 | y | 110,479 |
| confluent-kafka | PyPy 2.7 | 100 | n | 198,912 |
| confluent-kafka | PyPy 2.7 | 450 | n | 85,064 |
| confluent-kafka | PyPy 2.7 | 450 | y | 62,478 |
| kafka-cffi | PyPy 2.7 | 100 | n | 852,946 |
| kafka-cffi | PyPy 2.7 | 450| n | 435,655 |
| kafka-cffi | PyPy 2.7 | 450 | y | 263,587 |

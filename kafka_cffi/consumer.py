from kafka_cffi.utils import make_rd_conf, kafka_new
from ._rdkafka import lib, ffi


@ffi.def_extern()
def consumer_offset_commit_cb (rk, err, c_parts, opaque):
	pass


@ffi.def_extern()
def consumer_rebalance_cb (rk, err, c_parts, opaque):
	pass


class Consumer(object):

	def __init__(self, *args, **kwargs):
		rd_conf = make_rd_conf(*args, **kwargs)
		lib.rd_kafka_conf_set_offset_commit_cb(rd_conf,
			lib.consumer_offset_commit_cb)
		lib.rd_kafka_conf_set_rebalance_cb(rd_conf,
			lib.consumer_rebalance_cb)
		self.rk = kafka_new(lib.RD_KAFKA_CONSUMER, rd_conf)
		lib.rd_kafka_poll_set_consumer(self.rk)
		self.rk_consumer_queue = lib.rd_kafka_queue_get_consumer(self.rk)


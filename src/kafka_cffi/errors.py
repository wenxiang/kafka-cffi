from ._rdkafka import ffi, lib


class ConfigurationError(Exception):
    pass


class InitializationError(Exception):
    pass


class KafkaError(object):

    __slots__ = ('__resp_err_t',)

    _ALL_BROKERS_DOWN = -187
    _ASSIGN_PARTITIONS = -175
    _AUTHENTICATION = -169
    _BAD_COMPRESSION = -198
    _BAD_MSG = -199
    _CONFLICT = -173
    _CRIT_SYS_RESOURCE = -194
    _DESTROY = -197
    _EXISTING_SUBSCRIPTION = -176
    _FAIL = -196
    _FS = -189
    _INTR = -163
    _INVALID_ARG = -186
    _IN_PROGRESS = -178
    _ISR_INSUFF = -183
    _KEY_DESERIALIZATION = -160
    _KEY_SERIALIZATION = -162
    _MSG_TIMED_OUT = -192
    _NODE_UPDATE = -182
    _NOENT = -156
    _NOT_IMPLEMENTED = -170
    _NO_OFFSET = -168
    _OUTDATED = -167
    _PARTIAL = -158
    _PARTITION_EOF = -191
    _PREV_IN_PROGRESS = -177
    _QUEUE_FULL = -184
    _READ_ONLY = -157
    _RESOLVE = -193
    _REVOKE_PARTITIONS = -174
    _SSL = -181
    _STATE = -171
    _TIMED_OUT = -185
    _TIMED_OUT_QUEUE = -166
    _TRANSPORT = -195
    _UNDERFLOW = -155
    _UNKNOWN_GROUP = -179
    _UNKNOWN_PARTITION = -190
    _UNKNOWN_PROTOCOL = -171
    _UNKNOWN_TOPIC = -188
    _UNSUPPORTED_FEATURE = -165
    _VALUE_DESERIALIZATION = -159
    _VALUE_SERIALIZATION = -161
    _WAIT_CACHE = -164
    _WAIT_COORD = -180

    BROKER_NOT_AVAILABLE = 8
    CLUSTER_AUTHORIZATION_FAILED = 31
    CONCURRENT_TRANSACTIONS = 51
    DUPLICATE_SEQUENCE_NUMBER = 46
    GROUP_AUTHORIZATION_FAILED = 30
    GROUP_COORDINATOR_NOT_AVAILABLE = 15
    GROUP_LOAD_IN_PROGRESS = 14
    ILLEGAL_GENERATION = 22
    ILLEGAL_SASL_STATE = 34
    INCONSISTENT_GROUP_PROTOCOL = 23
    INVALID_COMMIT_OFFSET_SIZE = 28
    INVALID_CONFIG = 40
    INVALID_GROUP_ID = 24
    INVALID_MSG = 2
    INVALID_MSG_SIZE = 4
    INVALID_PARTITIONS = 37
    INVALID_PRODUCER_EPOCH = 47
    INVALID_PRODUCER_ID_MAPPING = 49
    INVALID_REPLICATION_FACTOR = 38
    INVALID_REPLICA_ASSIGNMENT = 39
    INVALID_REQUEST = 42
    INVALID_REQUIRED_ACKS = 21
    INVALID_SESSION_TIMEOUT = 26
    INVALID_TIMESTAMP = 32
    INVALID_TRANSACTION_TIMEOUT = 50
    INVALID_TXN_STATE = 48
    LEADER_NOT_AVAILABLE = 5
    MSG_SIZE_TOO_LARGE = 10
    NETWORK_EXCEPTION = 13
    NOT_CONTROLLER = 41
    NOT_COORDINATOR_FOR_GROUP = 16
    NOT_ENOUGH_REPLICAS = 19
    NOT_ENOUGH_REPLICAS_AFTER_APPEND = 20
    NOT_LEADER_FOR_PARTITION = 6
    NO_ERROR = 0
    OFFSET_METADATA_TOO_LARGE = 12
    OFFSET_OUT_OF_RANGE = 1
    OPERATION_NOT_ATTEMPTED = 55
    OUT_OF_ORDER_SEQUENCE_NUMBER = 45
    POLICY_VIOLATION = 44
    REBALANCE_IN_PROGRESS = 27
    RECORD_LIST_TOO_LARGE = 18
    REPLICA_NOT_AVAILABLE = 9
    REQUEST_TIMED_OUT = 7
    SECURITY_DISABLED = 54
    STALE_CTRL_EPOCH = 12
    TOPIC_ALREADY_EXISTS = 36
    TOPIC_AUTHORIZATION_FAILED = 29
    TOPIC_EXCEPTION = 17
    TRANSACTIONAL_ID_AUTHORIZATION_FAILED = 53
    TRANSACTION_COORDINATOR_FENCED = 52
    UNKNOWN = -1
    UNKNOWN_MEMBER_ID = 25
    UNKNOWN_TOPIC_OR_PART = 3
    UNSUPPORTED_FOR_MESSAGE_FORMAT = 43
    UNSUPPORTED_SASL_MECHANISM = 33
    UNSUPPORTED_VERSION = 35

    def __init__(self, resp_err_t):
        self.__resp_err_t = resp_err_t

    def code(self):
        return self.__resp_err_t

    def name(self):
        return ffi.string(lib.rd_kafka_err2name(self.__resp_err_t)).decode("utf8")

    def str(self):
        return ffi.string(lib.rd_kafka_err2str(self.__resp_err_t)).decode("utf8")

    def __repr__(self):
        return "{}: {}".format(self.name(), self.str())


class KafkaException(Exception):

    def __init__(self, err, *args, **kwargs):
        super(KafkaException, self).__init__(KafkaError(err), *args, **kwargs)

    def __repr__(self):
        return self.args[0]

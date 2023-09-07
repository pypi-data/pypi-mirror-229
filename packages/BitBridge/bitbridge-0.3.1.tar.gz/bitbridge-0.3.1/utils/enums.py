from enum import Enum


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class RPCGroup(str, Enum):
    BLOCKCHAIN = "blockchain"
    CONTROL = "control"
    NETWORK = "network"
    RAW_TRANSACTIONS = "raw_transactions"
    UTIL = "util"
    WALLET = "wallet"


class Mode(str, Enum):
    SYNC = "sync"
    ASYNC = "async"

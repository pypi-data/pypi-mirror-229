from bitbridge.rpc_delegate import RpcDelegate


class BaseRPC:
    def __init__(self, rpc_delegate: RpcDelegate):
        self.rpc_delegate = rpc_delegate

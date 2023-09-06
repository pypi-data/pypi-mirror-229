from bitbridge import BitBridgeFacade


def test_bridge_facade(bridge_facade_config):
    bridge = BitBridgeFacade(**bridge_facade_config)
    best_block_hash = bridge.blockchain.get_best_block_hash()
    print(best_block_hash)

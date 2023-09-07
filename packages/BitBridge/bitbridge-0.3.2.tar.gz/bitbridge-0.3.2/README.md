# BitBridge 🌉

BitBridge offers a seamless Python interface to the Bitcoin Core RPC, simplifying interactions with the Bitcoin protocol. With support for both synchronous and asynchronous operations, BitBridge is perfectly suited for diverse applications - from web platforms and backend services to data analytics tools. 

## 🌟 Features

- **Dual Mode Operations**: Supports both synchronous and asynchronous operations, giving you the flexibility to choose based on your application's needs.
  
- **Modularity at Core**: Designed with a modular architecture, BitBridge can easily be extended and integrated into a variety of systems.
  
- **Complete RPC Integration**: Comprehensive coverage of all RPC methods offered by Bitcoin Core, ensuring you have everything you need for Bitcoin interactions in one place.

## 🚀 Installation

```bash
pip install BitBridge
```

## 🎯 Quick Start

### Synchronous Mode:

```python
from bitbridge import BitBridgeFacade, BitBridgeConfig

# Configure RPC server details
config = BitBridgeConfig(url="http://127.0.0.1:8332", username="your_username", password="your_password")
bridge = BitBridgeFacade(config)

def fetch_best_block():
    # Retrieve the best block hash
    best_block_hash = bridge.blockchain.get_best_block_hash()
    # Additional operations...
```

### Asynchronous Mode:

```python
from bitbridge import AsyncBitBridgeFacade, BitBridgeConfig

# Configure RPC server details
config = BitBridgeConfig(url="http://127.0.0.1:8332", username="your_username", password="your_password")
bridge = AsyncBitBridgeFacade(config)

async def fetch_best_block():
    # Retrieve the best block hash
    best_block_hash = await bridge.blockchain.get_best_block_hash()
    # Additional operations...
```

## 🛠 Status

🚧 **Development Phase**: Please note that BitBridge is still in its initial development phase. Some features might be experimental.

## 📜 License

BitBridge is open-sourced under the [MIT License](https://github.com/godd0t/bitbridge/blob/main/LICENSE). 

# BitBridge

BitBridge is a modern Python interface to the Bitcoin Core RPC. It provides a seamless way to interact with Bitcoin's underlying protocol, offering both synchronous and asynchronous support. Whether you're building a web application, a backend service, or a data analysis tool, BitBridge makes it easy to integrate Bitcoin functionalities into your Python projects.

## Features

- **Synchronous & Asynchronous Support**: BitBridge is designed to work in both traditional synchronous environments and modern asynchronous frameworks.
  
- **Modular Design**: Easily extend and integrate BitBridge with other systems, thanks to its modular architecture.
  
- **Comprehensive RPC Coverage**: BitBridge aims to cover all the RPC methods provided by Bitcoin Core, making it a one-stop solution for all your Bitcoin interaction needs.

## Installation

```bash
pip install BitBridge
```

## Quick Start

```python
from bitbridge import BitBridgeFacade

# Initialize the facade with your RPC server details
bridge = BitBridgeFacade(url="http://127.0.0.1:8332", username="your_username", password="your_password")

# Fetch the best block hash
best_block_hash = bridge.blockchain.get_best_block_hash()
print(best_block_hash)
```

## Status

🚧 **Note**: BitBridge is currently in its initial development phase.

## License

[MIT License](LICENSE)

from bitbridge.rpc.config import BitBridgeConfig


def log_info(message: str):
    BitBridgeConfig.console.print(f"[blue]INFO:[/blue] {message}")


def log_error(message: str):
    BitBridgeConfig.console.print(f"[bold red]ERROR:[/bold red] {message}")

from typing import Optional, Callable
from rich.console import Console

from bitbridge.utils.enums import LogLevel
from bitbridge.utils.helpers import BaseSingleton


class BitBridgeConfig(BaseSingleton):
    default_max_retries: int = 0
    default_recovery_procedure: Optional[Callable] = None
    default_delay: Optional[int] = 0
    console = Console()

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        retries: int | None = None,
        timeout: int | None = None,
        logging_level: LogLevel = LogLevel.INFO,
    ):
        if not hasattr(self, "is_initialized"):
            self.url = url
            self.username = username
            self.password = password
            self.retries = retries
            self.timeout = timeout
            self.logging_level = logging_level
            self.is_initialized = True

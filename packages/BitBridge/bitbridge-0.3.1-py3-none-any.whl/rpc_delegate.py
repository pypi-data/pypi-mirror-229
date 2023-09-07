import httpx

from bitbridge.rpc.config import BitBridgeConfig
from bitbridge.utils.decorators import handle_exceptions, async_handle_exceptions
from bitbridge.utils.enums import Mode
from bitbridge.utils.exceptions import RPCError


class RpcDelegate:
    def __init__(self, config: BitBridgeConfig, mode: Mode = Mode.SYNC):
        self.config = config
        self._initial_params = {"jsonrpc": "2.0"}
        self._http_client = httpx.Client if mode == Mode.SYNC else httpx.AsyncClient

    def _get_auth(self):
        return httpx.BasicAuth(self.config.username, self.config.password)

    def _construct_payload(self, method: str, params: list | None = None):
        if params is None:
            params = []
        return {**self._initial_params, "method": method, "params": params}

    @handle_exceptions(exceptions=(httpx.HTTPError, RPCError))
    def send_request(
        self, method: str, params: list | None = None, append_to_url: str | None = None
    ):
        payload = self._construct_payload(method, params)
        if append_to_url is not None:
            self.config.url = f"{self.config.url}/wallet/{append_to_url}"
        response = self._http_client().post(
            self.config.url, json=payload, auth=self._get_auth()
        )
        print(self.config.url)
        response_content = response.json()
        # Check if the response contains an error
        if "error" in response_content and response_content["error"] is not None:
            raise RPCError(response_content["error"])
        return response.json()

    @async_handle_exceptions(exceptions=(httpx.HTTPError, RPCError))
    async def send_request_async(
        self, method: str, params: list | None = None, append_to_url: str | None = None
    ):
        payload = self._construct_payload(method, params)
        async with self._http_client() as client:
            if append_to_url is not None:
                self.config.url = f"{self.config.url}/wallet/{append_to_url}"
            response = await client.post(
                self.config.url, json=payload, auth=self._get_auth()
            )
            response_content = response.json()
            print(response_content)
            # Check if the response contains an error
            if "error" in response_content and response_content["error"] is not None:
                raise RPCError(response_content["error"])
            return response.json()

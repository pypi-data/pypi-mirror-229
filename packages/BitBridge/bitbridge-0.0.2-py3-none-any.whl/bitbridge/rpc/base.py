import httpx


class BitBridgeBaseRPC:
    def __init__(self, url: str, username: str, password: str):
        self._initial_params = {"jsonrpc": "2.0"}
        self.url = url
        self.username = username
        self.password = password

    def _get_auth(self):
        return httpx.BasicAuth(self.username, self.password)

    def _get_payload(self, method: str, params: list | None = None):
        if params is None:
            params = []
        return {**self._initial_params, "method": method, "params": params}

    def send_request(self, method: str, params: list | None = None):
        payload = self._get_payload(method, params)
        response = httpx.post(self.url, json=payload, auth=self._get_auth())
        response.raise_for_status()
        return response.json()

    async def send_request_async(self, method: str, params: list | None = None):
        payload = self._get_payload(method, params)
        async with httpx.AsyncClient() as client:
            response = await client.post(self.url, json=payload, auth=self._get_auth())
            response.raise_for_status()
            return response.json()

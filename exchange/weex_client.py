import time
import hmac
import hashlib
import base64
import json
import requests


class WeexClient:
    def __init__(self, api_key, secret_key, passphrase, base_url):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = base_url.rstrip("/")

    def _timestamp(self):
        return str(int(time.time() * 1000))

    def _sign(self, timestamp, method, path, query="", body=""):
        message = timestamp + method.upper() + path + query + body
        signature = hmac.new(
            self.secret_key.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(signature).decode()

    def _headers(self, signature, timestamp):
        return {
            "ACCESS-KEY": self.api_key,
            "ACCESS-SIGN": signature,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-PASSPHRASE": self.passphrase,
            "Content-Type": "application/json",
            "locale": "en-US"
        }

    def get(self, path, params=None, private=False):
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())

        timestamp = self._timestamp()
        signature = ""

        if private:
            signature = self._sign(timestamp, "GET", path, query, "")

        headers = self._headers(signature, timestamp) if private else {}
        url = self.base_url + path + query

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    def post(self, path, body, private=True):
        timestamp = self._timestamp()
        body_json = json.dumps(body)
        signature = self._sign(timestamp, "POST", path, "", body_json)
        headers = self._headers(signature, timestamp)

        url = self.base_url + path
        response = requests.post(url, headers=headers, data=body_json, timeout=10)
        response.raise_for_status()
        return response.json()

    @classmethod
    def from_env(cls):
        import os
        return cls(
            api_key=os.environ["WEEX_API_KEY"],
            secret_key=os.environ["WEEX_SECRET_KEY"],
            passphrase=os.environ["WEEX_PASSPHRASE"],
            base_url=os.getenv("WEEX_BASE_URL", "https://api-contract.weex.com")
        )

    def upload_ai_log(self, payload):
        """
        Uploads AI decision log to the exchange.
        """
        # In a real scenario this would post to the endpoint
        # return self.post("/capi/v2/ai/log", payload)
        return {"status": "success", "mock": True}

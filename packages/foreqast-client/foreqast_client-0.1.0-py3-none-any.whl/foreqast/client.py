"""Defines the client that composes requests to the ForeQast API."""
import warnings
from typing import Dict
from urllib.parse import urlencode

import requests
from pandas import DataFrame

from foreqast.vrp import Vehicle, VRP

_DEFAULT_BASE_URL = "http://127.0.0.1:5000/api"
_DEFAULT_TIMEOUT = 60


class Client:
    """The request client for the ForeQast API"""

    def __init__(
            self,
            api_key: str,
            base_url: str = _DEFAULT_BASE_URL,
            timeout: int = _DEFAULT_TIMEOUT
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._session = requests.Session()

        self._timeout = timeout
        self._requests_kwargs = {
            "headers": {
                "Content-type": "application/json",
                "Authorization": self._api_key,
            },
            "timeout": self._timeout,
        }

    def request(
            self,
            method: str,
            url: str,
            params: Dict = None,
            request_kwargs: Dict = None
    ):
        """Compose and send a request"""

        request_method = self._session.post if method == "POST" else self._session.get

        request_kwargs = request_kwargs or {}
        final_requests_kwargs = dict(self._requests_kwargs, **request_kwargs)

        if params and method == "POST":
            final_requests_kwargs["json"] = params

        if params and method == "GET":
            url = url + "?" + urlencode(list(params.items()))

        try:
            response = request_method(self._base_url + url, **final_requests_kwargs)
            if response.status_code != 200:
                raise ValueError(response.text)
            body = response.json()
            if body.get("status") == "ERROR":
                raise ValueError(body.get("message"))
            elif body.get("status") == "WARNING":
                warnings.warn(body.get("message"))
            return body["result"]
        except requests.exceptions.Timeout:
            return {}

    def vrp(
            self,
            depot_address: str,
            orders: DataFrame,
            vehicles: Dict[str, Vehicle],
    ) -> VRP:
        """Constructs a VRP instance"""
        return VRP(self, depot_address, orders, vehicles)

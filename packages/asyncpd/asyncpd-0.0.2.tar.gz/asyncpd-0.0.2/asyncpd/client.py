# Copyright 2023 Bradley Bonitatibus

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""API Client."""
from __future__ import annotations
from typing import Any

import httpx

from asyncpd.models.abilities import AbilitiesAPI
from asyncpd.models.addons import AddonsAPI
from asyncpd.models.analytics import AnalyticsAPI


class APIClient:
    """APIClient is the adapter for calling various PagerDuty API resources."""

    def __init__(self, token: str, base_url: str | None = None) -> None:
        """Initialize the API client.

        Args:
            token (str): API Token.
            base_url (str | None): Base URL.
        """
        base = base_url or "https://api.pagerduty.com"
        self.__client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=base,
            headers={
                "Authorization": f"Token {token}",
                "Accept": "application/vnd.pagerduty+json;version=2",
            },
        )

    async def request(
        self,
        method: str,
        endpoint: str,
        headers: dict[str, str] | None = None,
        data: dict | None = None,
        params: list[tuple[str, Any]] | None = None,
    ) -> httpx.Response:
        """Execute an async HTTP request to PagerDutys REST API."""
        if method in ("POST", "PUT") and headers is None:
            headers = {"Content-Type": "application/json"}

        return await self.__client.request(
            method=method, url=endpoint, data=data, headers=headers, params=params
        )

    async def aclose(self) -> None:
        """Closes the underlying HTTP client."""
        return await self.__client.aclose()

    @property
    def abilities(self) -> AbilitiesAPI:
        """Return an instance of the AbilitiesAPI resource."""
        return AbilitiesAPI(self)

    @property
    def addons(self) -> AddonsAPI:
        """Return an instance of the AddonsAPI resource."""
        return AddonsAPI(self)

    @property
    def analytics(self) -> AnalyticsAPI:
        """Return an instance of the AnalyticsAPI resource."""
        return AnalyticsAPI(self)

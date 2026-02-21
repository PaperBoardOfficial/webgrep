"""HTTP client with browser impersonation via curl_cffi."""

import random

from curl_cffi.requests import AsyncSession

CHROME_VERSIONS = [
    "chrome110", "chrome116", "chrome119", "chrome120",
    "chrome123", "chrome124", "chrome131", "chrome133a",
]


def random_impersonate() -> str:
    return random.choice(CHROME_VERSIONS)


async def fetch(
    url: str,
    *,
    method: str = "GET",
    params: dict | None = None,
    data: dict | None = None,
    headers: dict | None = None,
    cookies: dict | None = None,
    timeout: int = 10,
    proxy: str | None = None,
    session: AsyncSession | None = None,
) -> str:
    """Fetch a URL with browser impersonation. Returns response text."""
    impersonate = random_impersonate()

    if session:
        resp = await session.request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            impersonate=impersonate,
            proxy=proxy,
        )
        resp.raise_for_status()
        return resp.text

    async with AsyncSession() as s:
        resp = await s.request(
            method,
            url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            impersonate=impersonate,
            proxy=proxy,
        )
        resp.raise_for_status()
        return resp.text

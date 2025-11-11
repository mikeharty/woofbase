from httpx import AsyncClient, HTTPStatusError, Response, RequestError
from tenacity import (
    retry,
    retry_if_exception_type,
    wait_exponential_jitter,
    stop_after_attempt,
)
from common.log import Log
from common.env import get_env

OLIVE_API_MAX_RETRIES = int(get_env("OLIVE_API_MAX_RETRIES", "5"))
OLIVE_API_BASE_URL = get_env(
    "OLIVE_API_BASE_URL", "https://interview-api-olive.vercel.app/api/"
)
OLIVE_API_TIMEOUT = int(get_env("OLIVE_API_TIMEOUT", 30))


class OliveClient:
    def __init__(self):
        self.base_url = OLIVE_API_BASE_URL
        self.timeout = OLIVE_API_TIMEOUT
        self.client = AsyncClient(base_url=self.base_url, timeout=self.timeout)

    @retry(
        stop=stop_after_attempt(OLIVE_API_MAX_RETRIES),
        wait=wait_exponential_jitter(initial=1, max=10),
        retry=retry_if_exception_type(HTTPStatusError),
    )
    async def fetch_page(self, endpoint: str = "dogs", page: int = 1) -> Response:
        try:
            response = await self.client.get(
                f"/{endpoint}", params={"page": page}, timeout=self.timeout
            )
            response.raise_for_status()
            return response
        except RequestError as e:
            print(
                f"An error occurred while making GET request to {self.base_url}{endpoint}: {e}"
            )
            raise

    async def fetch_all(self, endpoint: str = "dogs") -> list[dict]:
        all_items = []
        page = 1

        while True:
            try:
                response = await self.fetch_page(endpoint=endpoint, page=page)
                items = response.json()
                if not isinstance(items, list):
                    raise ValueError("Response is not a list")
                if not len(items):
                    break
                all_items.extend(items)
                page += 1
            except RequestError as error:
                Log.error(
                    f"Unhandled exception occurred while fetching page {page}", error
                )
                break

        if not len(all_items):
            raise ValueError("No items were fetched from the API.")

        return all_items

    async def close(self):
        await self.client.aclose()

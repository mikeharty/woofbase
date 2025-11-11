import asyncio
import json
import random
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import httpx

REQUEST_LOG = "./clients/olive_requests.log"

DOG_WORDS = [
    "Paw",
    "Bark",
    "Doggo",
    "Woof",
    "Fetch",
    "Puppy",
    "Canine",
    "Mutt",
    "Hound",
    "Tail",
]

BROWSER_WORDS = [
    "Fox",
    "Explorer",
    "Navigator",
    "Browser",
    "Zilla",
    "Master",
    "Hunter",
    "Crawler",
    "Prowler",
    "Wagger",
]


@dataclass
class TestResult:
    page: Optional[int]
    attempt: int
    user_agent: str
    status_code: Optional[int]
    response_time: float
    json_valid: bool
    data_length: Any
    data_hash: Optional[int]
    response_size: int
    data: str
    query_params: Dict[str, Any]
    error: Optional[str] = None


BASE_URL = "https://interview-api-olive.vercel.app/api/dogs"


def make_user_agent() -> str:
    return (
        f"{random.choice(DOG_WORDS)}{random.choice(BROWSER_WORDS)}/"
        f"{random.randint(1,10)}.{random.randint(0,99)}"
    )


async def make_request(
    page: Optional[int] = None, limit: Optional[int] = None, **extra_params
) -> TestResult:
    user_agent = make_user_agent()
    headers = {"User-Agent": user_agent}
    params = extra_params.copy()
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit

    start_time = time.time()
    try:
        with open(REQUEST_LOG, "a") as f:
            f.write(
                f"Request: {BASE_URL}?{'&'.join([f'{k}={v}' for k,v in params.items()])}\n"
            )
            f.write(f"  Headers: {headers}\n")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(BASE_URL, headers=headers, params=params)
        response_time = time.time() - start_time

        try:
            data = response.json()
            json_valid = True
            data_length = len(data) if isinstance(data, list) else "N/A"
            data_hash = (
                hash(json.dumps(data, sort_keys=True))
                if isinstance(data, (list, dict))
                else None
            )
            data_serial = json.dumps(data) if isinstance(data, list) else str(data)
        except json.JSONDecodeError:
            data = response.text
            json_valid = False
            data_length = len(data)
            data_hash = None
            data_serial = str(data)

        result = TestResult(
            page=page,
            attempt=1,
            user_agent=user_agent,
            status_code=response.status_code,
            response_time=round(response_time, 3),
            json_valid=json_valid,
            data_length=data_length,
            data_hash=data_hash,
            response_size=len(response.content),
            data=data_serial,
            query_params=params,
        )

        with open(REQUEST_LOG, "a") as f:
            f.write(f"Response:\n{json.dumps(data, indent=2)}\n")

        return result
    except Exception as e:
        response_time = time.time() - start_time
        result = TestResult(
            page=page,
            attempt=1,
            user_agent=user_agent,
            status_code=None,
            response_time=round(response_time, 3),
            json_valid=False,
            data_length="N/A",
            data_hash=None,
            response_size=0,
            data="",
            query_params=params,
            error=str(e),
        )

        with open(REQUEST_LOG, "a") as f:
            f.write(f"ERROR: {str(e)}\n")

        return result


def print_result(result: TestResult):
    query_str = "&".join([f"{k}={v}" for k, v in result.query_params.items()])
    if query_str:
        query_str = f"?{query_str}"

    if result.error:
        print(f"  {query_str}: ERROR - {result.error} ({result.response_time}s)")
    else:
        data_info = (
            f"Data: {result.data_length}" if result.json_valid else "Invalid JSON"
        )
        print(
            f"  {query_str}: {result.status_code} - {data_info} ({result.response_time}s, {result.response_size} bytes)"
        )


async def test_limit_param(param_name: str = "limit") -> bool:
    print("\nTesting limit parameter...")

    test_limits = [1, 10, 20]

    for limit in test_limits:
        while True:
            result = await make_request(page=1, **{param_name: limit})
            print_result(result)

            if (
                result.status_code == 200
                and result.json_valid
                and isinstance(result.data_length, int)
            ):
                if result.data_length == limit:
                    print(f"  Limit {limit} appears to limit resuslts")
                    return True
                else:
                    print(f"  Limit {limit} did not limit results")
                break
            else:
                print(f"  Limit {limit} returned invalid data, retrying...")

                await asyncio.sleep(0.1)
                continue

        await asyncio.sleep(0.1)

    return False


async def test_limit_param_names():
    print("\nTesting limit parameter names...")

    param_names = [
        "limit",
        "count",
        "size",
        "num",
        "number",
        "results",
        "per_page",
        "max",
        "take",
    ]

    for param_name in param_names:
        print(f"\nTesting parameter name: '{param_name}'")
        result = await test_limit_param(param_name=param_name)
        if result:
            print(f"  Parameter name '{param_name}' appears to work for limit.")
        else:
            print(f"  Parameter name '{param_name}' does not limit results")
        await asyncio.sleep(0.1)


async def find_last_page():
    working_pages = []
    page = 1
    while True:
        result = await make_request(page=page)
        print_result(result)

        if result.status_code != 200:
            print(f"    Page {page} returned status {result.status_code} - retrying")
            continue
        if result.status_code == 200 and result.json_valid and result.data_length > 0:
            print(f"    Page {page} returned status 200 and has data, valid")
            working_pages.append(page)
            page += 1
        elif result.status_code == 200 and result.data_length == 0:
            print(f"    Page {page} returns empty array - candidate last page")
            break

        await asyncio.sleep(0.1)

    if not working_pages:
        print("No working pages found")
        return None

    last_working_page = max(working_pages)

    for page in range(last_working_page + 1, last_working_page + 5):
        result = await make_request(page=page)
        print_result(result)

        if result.status_code == 200 and result.data_length == 0:
            print(f"    Confirmed: Page {page} is empty")
        elif result.status_code == 200 and result.data_length > 0:
            print(f"    Unexpected: Page {page} not empty")
            last_working_page = page

        await asyncio.sleep(0.1)

    print(f"Found last working page: {last_working_page}")
    return last_working_page


async def test_response_consistency():
    print("\nTesting response consistency for first 10 pages...")

    for page in [1, 3, 7]:
        print(f"\n  Testing page {page}...")
        page_results = []

        for attempt in range(5):
            result = await make_request(page=page)
            page_results.append(result)
            print(f"    Attempt {attempt+1}: ", end="")
            print_result(result)
            await asyncio.sleep(0.2)

        successful_results = [
            r
            for r in page_results
            if r.status_code == 200 and r.json_valid and r.data_length > 0
        ]
        if successful_results:
            hashes = set(
                r.data_hash for r in successful_results if r.data_hash is not None
            )
            if len(hashes) == 1:
                print(f"    Page {page} is consistent")
            else:
                print(f"    Page {page} had {len(hashes)} unique responses")
        else:
            print(f"    Page {page} had no successful responses")


async def test_page_responses(test_page: int = 1):
    print(f"Testing page {test_page} repeatedly to look for patterns...")

    results = []
    for i in range(20):
        result = await make_request(page=test_page)
        results.append(result)
        status = result.status_code or "ERR"
        time_taken = result.response_time
        has_data = (
            result.data_length > 0
            if result.json_valid and isinstance(result.data_length, int)
            else False
        )
        print(
            f"  {i+1:2d}: {status:3} {time_taken:5.2f}s {'YES' if has_data else 'NO'}"
        )
        await asyncio.sleep(0.1)

    successful_results = [
        r
        for r in results
        if r.status_code == 200 and r.json_valid and r.data_length > 0
    ]

    long_responses = [r for r in results if r.response_time > 5]
    error_400 = sum(1 for r in results if r.status_code == 400)
    error_403 = sum(1 for r in results if r.status_code == 403)
    error_500 = sum(1 for r in results if r.status_code == 500)

    print(f"  Total requests: {len(results)}")
    print(f"  Successful (200 + contains list): {len(successful_results)}")
    print(f"  Long responses (>5s): {len(long_responses)}")
    print(f"  400 errors: {error_400}")
    print(f"  403 errors: {error_403}")
    print(f"  500 errors: {error_500}")

    if len(successful_results) > 1:
        hashes = set(r.data_hash for r in successful_results if r.data_hash is not None)
        if len(hashes) == 1:
            print("  All valid responses had identical data")
        else:
            print("  Responses had inconsistent data")


async def main():
    await test_limit_param_names()
    await test_response_consistency()
    await find_last_page()
    await test_page_responses(test_page=1)
    await test_page_responses(test_page=4)


if __name__ == "__main__":
    asyncio.run(main())

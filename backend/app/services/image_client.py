import os

import httpx


UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"


def search_unsplash_photo(
    query: str,
    *,
    per_page: int = 1,
) -> dict | None:
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        raise RuntimeError("UNSPLASH_ACCESS_KEY is not configured")

    headers = {
        "Authorization": f"Client-ID {access_key}",
        "Accept-Version": "v1",
    }

    params = {
        "query": query,
        "page": 1,
        "per_page": per_page,
        "orientation": "landscape",
        "content_filter": "high",
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.get(
            UNSPLASH_SEARCH_URL,
            headers=headers,
            params=params,
        )
        response.raise_for_status()

    data = response.json()
    results = data.get("results", [])
    if not results:
        return None

    return results[0]
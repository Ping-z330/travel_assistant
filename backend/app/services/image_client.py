import os

import httpx


PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"


def search_pexels_photo(
    query: str,
    *,
    per_page: int = 1,
) -> dict | None:
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY is not configured")

    headers = {
        "Authorization": api_key,
    }

    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
        "locale": "zh-CN",
    }

    with httpx.Client(timeout=6.0) as client:
        response = client.get(
            PEXELS_SEARCH_URL,
            headers=headers,
            params=params,
        )
        response.raise_for_status()

    data = response.json()
    photos = data.get("photos", [])
    if not photos:
        return None

    return photos[0]

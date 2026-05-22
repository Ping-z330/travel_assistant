from dataclasses import dataclass

from app.services.image_client import search_unsplash_photo


@dataclass
class ImageResult:
    image_url: str
    thumb_url: str
    alt_description: str
    photographer: str
    photographer_url: str
    download_location: str


def search_attraction_image(name: str, city: str) -> ImageResult | None:
    query = f"{name} {city}"
    photo = search_unsplash_photo(query)

    if not photo:
        return None

    urls = photo.get("urls", {})
    user = photo.get("user", {})
    user_links = user.get("links", {})
    links = photo.get("links", {})

    image_url = urls.get("regular", "") or urls.get("small", "")
    thumb_url = urls.get("small", "")
    alt_description = photo.get("alt_description", "") or ""
    photographer = user.get("name", "") or ""
    photographer_url = user_links.get("html", "") or ""
    download_location = links.get("download_location", "") or ""

    if not image_url:
        return None

    return ImageResult(
        image_url=image_url,
        thumb_url=thumb_url,
        alt_description=alt_description,
        photographer=photographer,
        photographer_url=photographer_url,
        download_location=download_location,
    )
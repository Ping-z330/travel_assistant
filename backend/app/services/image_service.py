from dataclasses import dataclass

from app.services.image_client import search_pexels_photo


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
    photo = search_pexels_photo(query)

    if not photo:
        return None

    sources = photo.get("src", {})

    image_url = sources.get("large", "") or sources.get("medium", "")
    thumb_url = sources.get("medium", "") or sources.get("small", "")
    alt_description = photo.get("alt", "") or ""
    photographer = photo.get("photographer", "") or ""
    photographer_url = photo.get("photographer_url", "") or ""
    download_location = photo.get("url", "") or ""

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

import httpx

from app.core.config import settings
from app.core.exceptions import BadRequestError


class ArticService:

    async def get_artwork(self, artwork_id: int) -> dict:
        if not settings.ARTIC_API_ENABLED:
            # Offline mode: the external API is behind a bot challenge and
            # unreachable from servers, so store a placeholder instead.
            return {
                "id": artwork_id,
                "title": f"Artwork #{artwork_id}",
                "artist_display": None,
                "image_url": None,
            }

        url =f"{settings.ARTIC_API_BASE_URL}/artworks/{artwork_id}"
        params = {"fields": "id,title,artist_display,image_id"}
        headers = {"AIC-User-Agent": "travel-planner (test-assessment)"}

        try:
            async with httpx.AsyncClient(timeout=settings.ARTIC_API_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=headers)
        except httpx.RequestError as exc:
            raise BadRequestError(
                f"Failed to connect to Art Institute API: {exc}"
            ) from exc

        if response.status_code == 404:
            raise BadRequestError(
                f"Artwork {artwork_id} not found in Art Institute API"
            )

        if not response.is_success:
            try:
                error_detail = response.json()
            except Exception:
                error_detail = response.text
            raise BadRequestError(
                f"Art Institute API error {response.status_code}: {error_detail}"
            )

        try:
            result = response.json()
            data = result.get("data", {})
        except Exception as exc:
            raise BadRequestError(
                f"Failed to parse Art Institute API response: {exc}"
            ) from exc

        if not data:
            raise BadRequestError(f"Artwork {artwork_id} returned empty data")

        image_id = data.get("image_id")

        return {
            "id": data.get("id", artwork_id),
            "title": data.get("title", "Untitled"),
            "artist_display": data.get("artist_display"),
            "image_url": (
                f"https://www.artic.edu/iiif/2/{image_id}/full/max/0/default.jpg"
                if image_id
                else None
            ),
        }

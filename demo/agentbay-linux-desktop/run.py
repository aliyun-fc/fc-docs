from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import urlparse


@dataclass(frozen=True)
class DemoConfig:
    api_key: str
    api_url: str
    domain: str
    template_id: str | None
    image: str | None
    template_name: str | None

    @classmethod
    def from_mapping(cls, values: Mapping[str, str]) -> "DemoConfig":
        required = ("E2B_API_KEY", "E2B_API_URL", "E2B_DOMAIN")
        missing = [key for key in required if not values.get(key)]
        if missing:
            raise ValueError(f"missing required variables: {', '.join(missing)}")

        template_id = values.get("E2B_DESKTOP_TEMPLATE_ID") or None
        image = values.get("E2B_DESKTOP_IMAGE") or None
        template_name = values.get("E2B_DESKTOP_TEMPLATE") or None
        if template_id:
            return cls(
                values["E2B_API_KEY"],
                values["E2B_API_URL"],
                values["E2B_DOMAIN"],
                template_id,
                None,
                None,
            )
        if not image:
            raise ValueError(
                "E2B_DESKTOP_IMAGE is required when E2B_DESKTOP_TEMPLATE_ID is not set"
            )
        if not template_name:
            raise ValueError(
                "E2B_DESKTOP_TEMPLATE is required when E2B_DESKTOP_TEMPLATE_ID is not set"
            )
        if template_name.startswith("desktop-v"):
            raise ValueError(
                "E2B_DESKTOP_TEMPLATE must not use the reserved desktop-v prefix"
            )
        return cls(
            values["E2B_API_KEY"],
            values["E2B_API_URL"],
            values["E2B_DOMAIN"],
            None,
            image,
            template_name,
        )


def validate_stream_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https":
        raise ValueError("desktop stream URL must use https")
    if not parsed.netloc or not parsed.hostname:
        raise ValueError("desktop stream URL must include a host")
    if parsed.path != "/vnc.html":
        raise ValueError("desktop stream URL path must be /vnc.html")

from __future__ import annotations

from dataclasses import dataclass
import os
import re
import sys
from typing import Mapping
from urllib.parse import urlparse, urlunparse


URL_PATTERN = re.compile(r"https?://[^\s]+", re.IGNORECASE)


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


def stage_message(stage: str, status: str, detail: str = "") -> str:
    """Format diagnostic output without exposing URL credentials or queries."""
    detail = URL_PATTERN.sub(_redact_url, detail)
    suffix = f" {detail}" if detail else ""
    return f"[{stage}] {status}{suffix}"


def _redact_url(match: re.Match[str]) -> str:
    parsed = urlparse(match.group())
    sanitized_netloc = parsed.netloc.rsplit("@", maxsplit=1)[-1]
    return urlunparse(parsed._replace(netloc=sanitized_netloc, query="", fragment=""))


def report(stage: str, status: str, detail: str = "") -> None:
    print(stage_message(stage, status, detail))


def build_template(config: DemoConfig) -> str:
    """Build the requested image and return its generated Template ID."""
    from e2b import Template, default_build_logger

    build = Template.build(
        Template().from_image(config.image),
        name=config.template_name,
        cpu_count=4,
        memory_mb=8192,
        on_build_logs=default_build_logger(),
    )
    report("template_build", "ok", f"template_id={build.template_id}")
    return build.template_id


def main() -> None:
    """Run the cloud diagnostic and clean up only resources this run created."""
    from dotenv import load_dotenv
    from e2b_desktop import Sandbox

    desktop = None
    stream_started = False
    cleanup_errors: list[Exception] = []
    stage = "configuration"

    try:
        load_dotenv()
        config = DemoConfig.from_mapping(os.environ)
        report("configuration", "ok", f"template reuse={bool(config.template_id)}")

        stage = "template_build"
        template_id = config.template_id or build_template(config)
        stage = "sandbox_create"
        desktop = Sandbox.create(template=template_id, timeout=900)
        report("sandbox_create", "ok", f"sandbox_id={desktop.sandbox_id}")

        stage = "runtime_command"
        result = desktop.commands.run("printf desktop-runtime-ok")
        if result.stdout != "desktop-runtime-ok":
            raise RuntimeError("unexpected command output")
        report("runtime_command", "ok")

        stage = "desktop_stream"
        desktop.stream.start(require_auth=True)
        stream_started = True
        auth_key = desktop.stream.get_auth_key()
        stream_url = desktop.stream.get_url(auth_key=auth_key)
        validate_stream_url(stream_url)
        report("desktop_stream", "ok", stream_url)

        stage = "screenshot"
        screenshot = desktop.screenshot()
        if not screenshot.startswith(b"\x89PNG\r\n\x1a\n"):
            raise RuntimeError("desktop screenshot is not PNG")
        report("screenshot", "ok")
    except Exception:
        report(stage, "failed")
        raise
    finally:
        primary_error = sys.exc_info()[0] is not None
        if desktop is not None:
            cleanup_detail = f"sandbox_id={desktop.sandbox_id}"
            if stream_started:
                try:
                    desktop.stream.stop()
                except Exception as error:
                    cleanup_errors.append(error)
                    cleanup_detail += f"; stream_stop={error}"
            try:
                desktop.kill()
            except Exception as error:
                cleanup_errors.append(error)
                cleanup_detail += f"; kill={error}"

        if cleanup_errors:
            report("cleanup", "failed", cleanup_detail)
            if not primary_error:
                raise cleanup_errors[0]
        elif desktop is not None:
            report("cleanup", "ok", cleanup_detail)


if __name__ == "__main__":
    main()

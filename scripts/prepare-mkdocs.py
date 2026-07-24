#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_SRC = ROOT / "_mkdocs_src"
SITE_DIR = ROOT / "_site"
CONFIG_PATH = ROOT / "mkdocs.generated.yml"
ROOT_NAV_PAGES = (
    ("首页", "README.md", "index.md"),
    ("English", "README.en-US.md", "README.en-US.md"),
    ("贡献指南", "CONTRIBUTING.md", "CONTRIBUTING.md"),
    ("Contributing", "CONTRIBUTING.en-US.md", "CONTRIBUTING.en-US.md"),
)


def main() -> None:
    reset_build_dirs()
    copy_content()
    nav = build_nav()
    write_config(nav)


def reset_build_dirs() -> None:
    for path in (DOCS_SRC, SITE_DIR):
        # The link itself is inside the repository and can be removed safely.
        # Resolve regular paths only, so an external link target is never touched.
        if path.is_symlink():
            path.unlink()
            continue
        resolved = path.resolve()
        if ROOT.resolve() not in resolved.parents:
            raise RuntimeError(f"Refusing to remove path outside repository: {path}")
        if path.exists():
            shutil.rmtree(path)
    DOCS_SRC.mkdir(parents=True)


def copy_content() -> None:
    for _, source_name, target_name in ROOT_NAV_PAGES:
        source = ROOT / source_name
        if not source.is_file():
            raise FileNotFoundError(f"Required navigation page is missing: {source}")
        target = DOCS_SRC / target_name
        if source_name == "README.en-US.md":
            text = source.read_text(encoding="utf-8").replace("(README.md)", "(index.md)")
            target.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(source, target)

    for name in ("docs", "assets"):
        source = ROOT / name
        if source.exists():
            shutil.copytree(source, DOCS_SRC / name)

    license_file = ROOT / "LICENSE"
    if license_file.exists():
        shutil.copy2(license_file, DOCS_SRC / "LICENSE")


def build_nav() -> list[dict[str, str | list]]:
    nav: list[dict[str, str | list]] = [
        {label: target_name} for label, _, target_name in ROOT_NAV_PAGES
    ]

    docs_nav: list[dict[str, str | list]] = []
    zh_nav = nav_for_directory(DOCS_SRC / "docs" / "zh-CN")
    en_nav = nav_for_directory(DOCS_SRC / "docs" / "en-US")
    if zh_nav:
        docs_nav.append({"中文文档": zh_nav})
    if en_nav:
        docs_nav.append({"English Docs": en_nav})
    if docs_nav:
        nav.append({"文档": docs_nav})

    return nav


def nav_for_directory(directory: Path) -> list[dict[str, str | list]]:
    entries: list[dict[str, str | list]] = []
    if not directory.exists():
        return entries

    directories = sorted(
        [path for path in directory.iterdir() if path.is_dir()],
        key=sort_path,
    )
    files = sorted(
        [path for path in directory.iterdir() if path.is_file() and path.suffix == ".md"],
        key=sort_path,
    )

    file_labels: list[tuple[str, str]] = []
    for file_path in files:
        text = file_path.read_text(encoding="utf-8")
        label = extract_nav_title(text) or extract_title(text) or clean_label(file_path.stem)
        file_labels.append((label, clean_label(file_path.stem)))

    for file_path, label in zip(files, disambiguate_labels(file_labels), strict=True):
        entries.append({label: relative_docs_path(file_path)})

    for child_dir in directories:
        child_entries = nav_for_directory(child_dir)
        if child_entries:
            entries.append({clean_label(child_dir.name): child_entries})

    return entries


def write_config(nav: list[dict[str, str | list]]) -> None:
    CONFIG_PATH.write_text(
        "\n".join(
            [
                "site_name: 阿里云函数计算官方文档",
                "site_url: https://aliyun-fc.github.io/fc-docs/",
                "repo_url: https://github.com/aliyun-fc/fc-docs",
                "repo_name: aliyun-fc/fc-docs",
                "docs_dir: _mkdocs_src",
                "site_dir: _site",
                "use_directory_urls: true",
                "theme:",
                "  name: material",
                "  language: zh",
                "  features:",
                "    - navigation.instant",
                "    - navigation.tracking",
                "    - navigation.sections",
                "    - navigation.indexes",
                "    - navigation.prune",
                "    - navigation.top",
                "    - toc.follow",
                "    - search.suggest",
                "    - search.highlight",
                "  palette:",
                "    - scheme: default",
                "      primary: blue",
                "      accent: light blue",
                "plugins:",
                "  - search:",
                "      lang:",
                "        - zh",
                "        - en",
                "  - optimize:",
                "      enabled: !ENV [CI, false]",
                "markdown_extensions:",
                "  - admonition",
                "  - attr_list",
                "  - md_in_html",
                "  - tables",
                "  - toc:",
                "      permalink: true",
                "  - pymdownx.details",
                "  - pymdownx.superfences",
                "validation:",
                "  links:",
                "    absolute_links: info",
                "    unrecognized_links: warn",
                "    anchors: warn",
                "nav:",
                render_nav_yaml(nav, indent=2),
                "",
            ]
        ),
        encoding="utf-8",
    )


def render_nav_yaml(items: list[dict[str, str | list]], indent: int) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for item in items:
        for label, value in item.items():
            if isinstance(value, list):
                lines.append(f"{prefix}- {yaml_string(label)}:")
                lines.append(render_nav_yaml(value, indent + 2))
            else:
                lines.append(f"{prefix}- {yaml_string(label)}: {yaml_string(value)}")
    return "\n".join(lines)


def relative_docs_path(path: Path) -> str:
    return path.relative_to(DOCS_SRC).as_posix()


def extract_title(text: str) -> str | None:
    for line in text.removeprefix("\ufeff").splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def extract_nav_title(text: str) -> str | None:
    lines = text.removeprefix("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        return None

    nav_title: str | None = None
    for line in lines[1:]:
        if line == "---":
            return nav_title
        match = re.match(r"^nav_title:\s*(.+?)\s*$", line)
        if match:
            nav_title = match.group(1).strip("\"'").strip() or None
    return None


def disambiguate_labels(labels: list[tuple[str, str]]) -> list[str]:
    preferred_counts = Counter(preferred for preferred, _ in labels)
    used: set[str] = set()
    result: list[str] = []

    for preferred, fallback in labels:
        base = fallback if preferred_counts[preferred] > 1 else preferred
        label = base
        suffix = 2
        while label in used:
            label = f"{base} ({suffix})"
            suffix += 1
        used.add(label)
        result.append(label)

    return result


def clean_label(value: str) -> str:
    value = re.sub(r"^\d+[.、_-]*", "", value)
    return value.replace("_", " ").strip() or "Untitled"


def sort_path(path: Path) -> tuple[str, ...]:
    return tuple(path.relative_to(DOCS_SRC).parts)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    main()

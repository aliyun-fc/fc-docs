#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath
from typing import NamedTuple
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
ASSETS_DIR = ROOT / "assets"
REFERENCE_DEFINITION = re.compile(
    r"^[ \t]{0,3}\[(?P<label>[^\]\n]+)\]:[ \t]*(?P<body>[^\n]*)$",
    re.MULTILINE,
)
INLINE_CODE = re.compile(r"(`+).*?\1", re.DOTALL)
HTML_MEDIA = re.compile(
    r"(?:src|poster)\s*=\s*(?P<quote>[\"'])(?P<target>.*?)\1",
    re.IGNORECASE,
)
HEADING = re.compile(r"^(?P<marks>#{1,6})\s+.+?\s*$")
UNSTABLE_ANCHOR = re.compile(r"^_\d*$")
EXTERNAL_PREFIXES = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")
SITE_ROOT_FILES = {
    "": "README.md",
    "index": "README.md",
    "index.md": "README.md",
    "README.en-US": "README.en-US.md",
    "README.en-US.md": "README.en-US.md",
    "CONTRIBUTING": "CONTRIBUTING.md",
    "CONTRIBUTING.md": "CONTRIBUTING.md",
    "CONTRIBUTING.en-US": "CONTRIBUTING.en-US.md",
    "CONTRIBUTING.en-US.md": "CONTRIBUTING.en-US.md",
    "LICENSE": "LICENSE",
}
SITE_PATH_PREFIX = "fc-docs"


class MarkdownLink(NamedTuple):
    target: str
    is_media: bool
    offset: int


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check documentation structure and local references."
    )
    parser.add_argument(
        "--max-asset-mb",
        type=float,
        default=8.0,
        help="Reject individual assets larger than this value (default: 8 MiB).",
    )
    args = parser.parse_args()

    errors: list[str] = []
    referenced_assets: set[Path] = set()
    markdown_files = sorted(DOCS_DIR.rglob("*.md"))
    link_sources = markdown_files + [ROOT / "README.md", ROOT / "README.en-US.md"]
    link_sources.extend(
        path
        for path in (ROOT / "CONTRIBUTING.md", ROOT / "CONTRIBUTING.en-US.md")
        if path.exists()
    )

    check_paths(errors)
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        check_headings(path, text, errors)
        check_local_references(path, text, errors, referenced_assets)

    for path in link_sources[len(markdown_files) :]:
        check_local_references(path, path.read_text(encoding="utf-8"), errors, referenced_assets)

    max_bytes = int(args.max_asset_mb * 1024 * 1024)
    assets = {
        path.resolve()
        for path in ASSETS_DIR.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    }
    for path in sorted(assets):
        if path.stat().st_size > max_bytes:
            errors.append(
                f"{relative(path)}: asset is {path.stat().st_size / 1024 / 1024:.1f} MiB; "
                f"limit is {args.max_asset_mb:g} MiB"
            )

    unreferenced = sorted(assets - referenced_assets)
    if unreferenced:
        print(
            f"WARN: {len(unreferenced)} asset files are not referenced "
            "by Markdown or HTML media tags."
        )

    if errors:
        print("Documentation checks failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        f"OK: checked {len(markdown_files)} Markdown files, "
        f"{len(assets)} assets, and all local references."
    )
    return 0


def check_paths(errors: list[str]) -> None:
    for base in (DOCS_DIR, ASSETS_DIR):
        for path in base.rglob("*"):
            if any(part != part.strip() for part in path.relative_to(ROOT).parts):
                errors.append(
                    f"{relative(path)}: path component has leading or trailing whitespace"
                )


def check_headings(path: Path, text: str, errors: list[str]) -> None:
    headings: list[tuple[int, int]] = []
    for line_number, line in visible_lines(text):
        match = HEADING.match(line)
        if match:
            headings.append((len(match.group("marks")), line_number))

    h1_count = sum(level == 1 for level, _ in headings)
    if h1_count != 1:
        errors.append(f"{relative(path)}: expected one H1 heading, found {h1_count}")

    previous_level: int | None = None
    for level, line_number in headings:
        if previous_level is not None and level > previous_level + 1:
            errors.append(
                f"{relative(path)}:{line_number}: heading jumps from H{previous_level} to H{level}"
            )
        previous_level = level


def check_local_references(
    path: Path,
    text: str,
    errors: list[str],
    referenced_assets: set[Path],
) -> None:
    visible = "\n".join(line for _, line in visible_lines(text))
    for link in extract_markdown_links(visible):
        check_target(
            path,
            visible,
            link.offset,
            link.target,
            link.is_media,
            errors,
            referenced_assets,
        )

    for match in HTML_MEDIA.finditer(visible):
        target = match.group("target").strip()
        check_target(path, visible, match.start(), target, True, errors, referenced_assets)


def check_target(
    source: Path,
    text: str,
    offset: int,
    raw_target: str,
    is_media: bool,
    errors: list[str],
    referenced_assets: set[Path],
) -> None:
    if raw_target.startswith(EXTERNAL_PREFIXES):
        return

    line_number = text[:offset].count("\n") + 1
    if is_unstable_anchor_target(raw_target):
        errors.append(
            f"{relative(source)}:{line_number}: unstable generated anchor; "
            f"use an explicit semantic anchor: {raw_target}"
        )
    if raw_target.startswith("#"):
        return

    target = raw_target
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = unquote(target.split("#", 1)[0].split("?", 1)[0].strip())
    if not target:
        return

    if target.startswith("/"):
        candidate = resolve_site_absolute_target(target)
        if candidate is None:
            errors.append(
                f"{relative(source)}:{line_number}: site-absolute target is not "
                f"published: {raw_target}"
            )
            return
    else:
        candidate = source.parent / target
    candidate = candidate.resolve()
    if ROOT.resolve() not in candidate.parents and candidate != ROOT.resolve():
        errors.append(
            f"{relative(source)}:{line_number}: local reference escapes the "
            f"repository: {raw_target}"
        )
        return

    exists = candidate.exists()
    if not exists and not is_media and not candidate.suffix:
        exists = candidate.with_suffix(".md").exists() or (candidate / "index.md").exists()
    if not exists:
        kind = "media" if is_media else "document"
        errors.append(f"{relative(source)}:{line_number}: missing local {kind}: {raw_target}")
        return

    if is_media and ASSETS_DIR.resolve() in candidate.parents:
        referenced_assets.add(candidate)


def is_unstable_anchor_target(target: str) -> bool:
    if target.startswith(EXTERNAL_PREFIXES) or "#" not in target:
        return False
    return bool(UNSTABLE_ANCHOR.fullmatch(unquote(target.rsplit("#", 1)[1])))


def resolve_site_absolute_target(target: str) -> Path | None:
    relative_target = unquote(target.lstrip("/"))
    path = PurePosixPath(relative_target)
    if ".." in path.parts:
        return None
    if path.parts and path.parts[0] == SITE_PATH_PREFIX:
        path = PurePosixPath(*path.parts[1:])

    normalized = path.as_posix()
    if normalized == ".":
        normalized = ""
    root_file = SITE_ROOT_FILES.get(normalized)
    if root_file:
        return ROOT / root_file
    if path.parts and path.parts[0] in {"docs", "assets"}:
        return ROOT.joinpath(*path.parts)
    return None


def extract_markdown_links(text: str) -> list[MarkdownLink]:
    definitions, definition_ranges = parse_reference_definitions(text)
    visible = mask_inline_code(text)
    links: list[MarkdownLink] = []
    range_starts = {start: end for start, end in definition_ranges}
    index = 0

    while index < len(visible):
        definition_end = range_starts.get(index)
        if definition_end is not None:
            index = definition_end
            continue

        is_media = visible.startswith("![", index)
        if is_media:
            label_start = index + 2
        elif visible[index] == "[" and (index == 0 or visible[index - 1] != "!"):
            label_start = index + 1
        else:
            index += 1
            continue

        label_end = find_matching_bracket(visible, label_start)
        if label_end is None:
            index += 1
            continue

        label = visible[label_start:label_end]
        following = label_end + 1
        if following < len(visible) and visible[following] == "(":
            parsed = parse_inline_destination(visible, following + 1)
            if parsed is not None:
                target, end = parsed
                links.append(MarkdownLink(target, is_media, index))
                index = end
                continue
        elif following < len(visible) and visible[following] == "[":
            reference_end = find_matching_bracket(visible, following + 1)
            if reference_end is not None:
                reference = visible[following + 1 : reference_end] or label
                definition = definitions.get(normalize_reference_label(reference))
                if definition:
                    links.append(MarkdownLink(definition, is_media, index))
                index = reference_end + 1
                continue
        else:
            definition = definitions.get(normalize_reference_label(label))
            if definition:
                links.append(MarkdownLink(definition, is_media, index))
                index = label_end + 1
                continue

        index = label_end + 1

    return links


def parse_reference_definitions(text: str) -> tuple[dict[str, str], list[tuple[int, int]]]:
    definitions: dict[str, str] = {}
    ranges: list[tuple[int, int]] = []
    for match in REFERENCE_DEFINITION.finditer(text):
        target = parse_reference_destination(match.group("body"))
        if target is not None:
            definitions.setdefault(normalize_reference_label(match.group("label")), target)
        ranges.append((match.start(), match.end()))
    return definitions, ranges


def parse_reference_destination(body: str) -> str | None:
    body = body.lstrip()
    if not body:
        return None
    if body.startswith("<"):
        closing = find_unescaped(body, ">", 1)
        return body[1:closing] if closing is not None else None

    depth = 0
    index = 0
    while index < len(body):
        character = body[index]
        if character == "\\":
            index += 2
            continue
        if character == "(":
            depth += 1
        elif character == ")" and depth:
            depth -= 1
        elif character.isspace() and depth == 0:
            break
        index += 1
    return body[:index] or None


def parse_inline_destination(text: str, start: int) -> tuple[str, int] | None:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    if index >= len(text):
        return None

    if text[index] == "<":
        closing = find_unescaped(text, ">", index + 1)
        if closing is None:
            return None
        target = text[index + 1 : closing]
        end = find_inline_link_end(text, closing + 1)
        return (target, end) if end is not None else None

    target_start = index
    depth = 0
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == "(":
            depth += 1
        elif character == ")":
            if depth == 0:
                return text[target_start:index], index + 1
            depth -= 1
        elif character.isspace() and depth == 0:
            target = text[target_start:index]
            end = find_inline_link_end(text, index)
            return (target, end) if target and end is not None else None
        elif character == "\n" and depth == 0:
            return None
        index += 1
    return None


def find_inline_link_end(text: str, start: int) -> int | None:
    index = start
    while index < len(text) and text[index].isspace():
        index += 1
    if index < len(text) and text[index] == ")":
        return index + 1
    if index >= len(text) or text[index] not in {'"', "'", "("}:
        return None

    opening = text[index]
    closing = ")" if opening == "(" else opening
    end_title = find_unescaped(text, closing, index + 1)
    if end_title is None:
        return None
    index = end_title + 1
    while index < len(text) and text[index].isspace():
        index += 1
    return index + 1 if index < len(text) and text[index] == ")" else None


def find_matching_bracket(text: str, start: int) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if character == "[":
            depth += 1
        elif character == "]":
            if depth == 0:
                return index
            depth -= 1
        elif character == "\n":
            return None
        index += 1
    return None


def find_unescaped(text: str, character: str, start: int) -> int | None:
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == character:
            return index
        index += 1
    return None


def normalize_reference_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.strip()).casefold()


def mask_inline_code(text: str) -> str:
    return INLINE_CODE.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), text)


def visible_lines(text: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_fence = False
    fence = ""
    for line_number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        marker = (
            "```"
            if stripped.startswith("```")
            else ("~~~" if stripped.startswith("~~~") else "")
        )
        if marker:
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
            result.append((line_number, ""))
            continue
        result.append((line_number, "" if in_fence else line))
    return result


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())

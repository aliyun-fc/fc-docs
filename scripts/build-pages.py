#!/usr/bin/env python3
from __future__ import annotations

import html
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit, urlunsplit

try:
    import markdown
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: Markdown. Install with "
        "`python -m pip install -r requirements-pages.txt`."
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
ASSETS_ROOT = ROOT / "assets"

MARKDOWN_EXTENSIONS = [
    "extra",
    "fenced_code",
    "tables",
    "toc",
    "sane_lists",
]

SKIP_DIRS = {
    ".git",
    ".github",
    "_site",
    "node_modules",
    "__pycache__",
}


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    markdown_files = collect_markdown_files()
    page_links = {source: output_path_for(source) for source in markdown_files}
    page_titles = {
        source: extract_title(source.read_text(encoding="utf-8")) or clean_label(source.stem)
        for source in markdown_files
    }

    copy_static_files()
    write_styles()

    for source in markdown_files:
        render_markdown_page(
            source,
            page_links[source],
            markdown_files,
            page_links,
            page_titles,
        )


def collect_markdown_files() -> list[Path]:
    files = [
        path
        for path in ROOT.rglob("*.md")
        if not should_skip(path)
    ]
    return sorted(files, key=lambda path: sort_key(path.relative_to(ROOT)))


def should_skip(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return any(part in SKIP_DIRS for part in rel.parts)


def output_path_for(source: Path) -> Path:
    rel = source.relative_to(ROOT)
    if rel.name == "README.md":
        rel = rel.with_name("index.md")
    return OUT / rel.with_suffix(".html")


def copy_static_files() -> None:
    for name in ("LICENSE",):
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, OUT / name)

    if ASSETS_ROOT.exists():
        shutil.copytree(ASSETS_ROOT, OUT / "assets", dirs_exist_ok=True)


def write_styles() -> None:
    style_dir = OUT / "_static"
    style_dir.mkdir(parents=True, exist_ok=True)
    (style_dir / "style.css").write_text(
        """
:root {
  color-scheme: light;
  --bg: #f7f8fa;
  --panel: #ffffff;
  --text: #172033;
  --muted: #667085;
  --border: #d9dee7;
  --accent: #0b5cad;
  --code-bg: #f2f4f7;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: var(--text);
  background: var(--bg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  line-height: 1.65;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
  padding: 24px 18px;
  border-right: 1px solid var(--border);
  background: var(--panel);
}

.brand {
  display: block;
  margin: 0 0 18px;
  color: var(--text);
  font-weight: 700;
}

.nav-heading {
  margin: 0 0 10px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
}

.nav-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.nav-list li {
  margin: 0;
}

.nav-section,
.nav-list a {
  display: block;
  overflow: hidden;
  padding: 4px 0;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-section {
  margin-top: 8px;
  color: var(--text);
  font-weight: 700;
}

.nav-list a {
  color: var(--muted);
}

.nav-list a:hover {
  color: var(--accent);
}

.nav-list a.active {
  color: var(--accent);
  font-weight: 700;
}

.nav-depth-1 {
  padding-left: 12px;
}

.nav-depth-2 {
  padding-left: 24px;
}

.nav-depth-3 {
  padding-left: 36px;
}

.nav-depth-4,
.nav-depth-5,
.nav-depth-6 {
  padding-left: 48px;
}

.content {
  min-width: 0;
  padding: 40px 48px 80px;
}

.doc {
  max-width: 980px;
}

.doc h1,
.doc h2,
.doc h3 {
  line-height: 1.28;
}

.doc h1 {
  margin-top: 0;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.doc img {
  max-width: 100%;
  height: auto;
}

.doc table {
  display: block;
  width: max-content;
  max-width: 100%;
  overflow: auto;
  border-collapse: collapse;
}

.doc th,
.doc td {
  padding: 8px 10px;
  border: 1px solid var(--border);
  vertical-align: top;
}

.doc code {
  padding: 0.15em 0.35em;
  border-radius: 4px;
  background: var(--code-bg);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}

.doc pre {
  overflow: auto;
  padding: 16px;
  border-radius: 6px;
  background: var(--code-bg);
}

.doc pre code {
  padding: 0;
  background: transparent;
}

@media (max-width: 860px) {
  .layout {
    display: block;
  }

  .sidebar {
    position: relative;
    height: auto;
    max-height: 50vh;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }

  .content {
    padding: 28px 20px 56px;
  }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def render_markdown_page(
    source: Path,
    output: Path,
    markdown_files: list[Path],
    page_links: dict[Path, Path],
    page_titles: dict[Path, str],
) -> None:
    rel_source = source.relative_to(ROOT)
    markdown_text = source.read_text(encoding="utf-8")
    markdown_text = rewrite_markdown_links(markdown_text, source)
    body = markdown.markdown(
        markdown_text,
        extensions=MARKDOWN_EXTENSIONS,
        output_format="html5",
    )
    body = rewrite_html_urls(body, source)

    title = page_titles[source]
    depth = len(output.relative_to(OUT).parents) - 1
    static_prefix = "../" * depth

    output.parent.mkdir(parents=True, exist_ok=True)
    nav = render_nav(markdown_files, page_links, page_titles, output)
    output.write_text(
        page_template(
            title=title,
            body=body,
            nav=nav,
            stylesheet=f"{static_prefix}_static/style.css",
            home_href=f"{static_prefix}index.html",
            source_path=rel_source.as_posix(),
        ),
        encoding="utf-8",
    )


def rewrite_markdown_links(text: str, source: Path) -> str:
    pattern = re.compile(r"(!?\[[^\]]*\]\()([^)\s]+(?:%20[^)]*)?)(\))")

    def replace(match: re.Match[str]) -> str:
        prefix, target, suffix = match.groups()
        if prefix.startswith("!"):
            return match.group(0)
        rewritten = rewrite_url(target, source)
        return f"{prefix}{rewritten}{suffix}"

    return pattern.sub(replace, text)


def rewrite_html_urls(body: str, source: Path) -> str:
    pattern = re.compile(r'(href|src)="([^"]+)"')

    def replace(match: re.Match[str]) -> str:
        attr, target = match.groups()
        rewritten = rewrite_url(target, source)
        return f'{attr}="{html.escape(rewritten, quote=True)}"'

    return pattern.sub(replace, body)


def rewrite_url(target: str, source: Path) -> str:
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc:
        return target

    path = unquote(parsed.path)
    if not path:
        return target

    if path.endswith(".md"):
        path = path[:-3] + ".html"

    if path.startswith("/"):
        new_path = quote(path, safe="/%")
    else:
        new_path = quote(path, safe="/%")

    return urlunsplit(("", "", new_path, parsed.query, parsed.fragment))


def render_nav(
    markdown_files: list[Path],
    page_links: dict[Path, Path],
    page_titles: dict[Path, str],
    current_output: Path,
) -> str:
    items = []
    previous_dirs: tuple[str, ...] = ()
    for source in markdown_files:
        rel = source.relative_to(ROOT)
        current_dirs = rel.parts[:-1]
        common = common_prefix_len(previous_dirs, current_dirs)
        for depth, part in enumerate(current_dirs[common:], start=common):
            label = directory_label(part)
            items.append(
                '<li>'
                f'<span class="nav-section nav-depth-{depth}" '
                f'title="{html.escape("/".join(current_dirs[: depth + 1]), quote=True)}">'
                f'{html.escape(label)}</span>'
                '</li>'
            )
        previous_dirs = current_dirs

        title = page_titles[source]
        href = relative_href(page_links[source], current_output.parent)
        depth = max(0, len(rel.parts) - 1)
        active = " active" if page_links[source] == current_output else ""
        items.append(
            '<li>'
            f'<a class="nav-depth-{depth}{active}" href="{href}" '
            f'title="{html.escape(rel.as_posix(), quote=True)}">'
            f'{html.escape(title)}</a>'
            '</li>'
        )
    return "\n".join(items)


def page_template(
    *,
    title: str,
    body: str,
    nav: str,
    stylesheet: str,
    home_href: str,
    source_path: str,
) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} - 阿里云函数计算官方文档</title>
  <link rel="stylesheet" href="{html.escape(stylesheet, quote=True)}">
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <a class="brand" href="{html.escape(home_href, quote=True)}">阿里云函数计算官方文档</a>
      <div class="nav-heading">目录</div>
      <ul class="nav-list">
{nav}
      </ul>
    </aside>
    <main class="content">
      <article class="doc" data-source="{html.escape(source_path, quote=True)}">
{body}
      </article>
    </main>
  </div>
</body>
</html>
"""


def extract_title(text: str) -> str | None:
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def clean_label(value: str) -> str:
    value = re.sub(r"^\d+[.、_-]*", "", value)
    return value.strip() or "Untitled"


def directory_label(value: str) -> str:
    labels = {
        "docs": "文档",
        "zh-CN": "中文文档",
        "en-US": "English Docs",
    }
    return labels.get(value, clean_label(value))


def common_prefix_len(left: tuple[str, ...], right: tuple[str, ...]) -> int:
    count = 0
    for left_part, right_part in zip(left, right):
        if left_part != right_part:
            break
        count += 1
    return count


def relative_href(target: Path, start: Path) -> str:
    rel = Path(os.path.relpath(target, start=start)).as_posix()
    return quote(rel, safe="/%")


def sort_key(path: Path) -> tuple[str, ...]:
    parts = path.parts
    if path.name == "README.md":
        return ("0",)
    if path.name == "README.en-US.md":
        return ("1",)
    if parts[:2] == ("docs", "zh-CN"):
        return ("2", *natural_sort_parts(parts))
    if parts[:2] == ("docs", "en-US"):
        return ("3", *natural_sort_parts(parts))
    return ("4", *natural_sort_parts(parts))


def natural_sort_parts(parts: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(part.casefold() for part in parts)


if __name__ == "__main__":
    main()

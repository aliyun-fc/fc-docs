from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "check-docs.py"
SPEC = importlib.util.spec_from_file_location("check_docs", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {MODULE_PATH}")
check_docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_docs)


class CheckDocsTest(unittest.TestCase):
    def test_detects_unstable_local_anchor(self) -> None:
        self.assertTrue(check_docs.is_unstable_anchor_target("#_2"))
        self.assertTrue(check_docs.is_unstable_anchor_target("other.md#_12"))

    def test_allows_semantic_and_external_anchors(self) -> None:
        self.assertFalse(check_docs.is_unstable_anchor_target("#使用限制"))
        self.assertFalse(
            check_docs.is_unstable_anchor_target("https://example.com/guide/#_2")
        )

    def test_extracts_nested_parentheses_and_reference_links(self) -> None:
        text = """\
[Wikipedia](https://example.com/Function_(mathematics))
[Guide][docs]
![Diagram][image]
[docs][]
[docs]

[docs]: docs/guide_(advanced).md
[image]: assets/diagram_(dark).png
"""
        links = check_docs.extract_markdown_links(text)

        self.assertEqual(
            [(link.target, link.is_media) for link in links],
            [
                ("https://example.com/Function_(mathematics)", False),
                ("docs/guide_(advanced).md", False),
                ("assets/diagram_(dark).png", True),
                ("docs/guide_(advanced).md", False),
                ("docs/guide_(advanced).md", False),
            ],
        )

    def test_site_absolute_targets_only_resolve_published_content(self) -> None:
        self.assertEqual(
            check_docs.resolve_site_absolute_target("/docs/zh-CN/example.md"),
            check_docs.ROOT / "docs/zh-CN/example.md",
        )
        self.assertEqual(
            check_docs.resolve_site_absolute_target("/CONTRIBUTING"),
            check_docs.ROOT / "CONTRIBUTING.md",
        )
        self.assertEqual(
            check_docs.resolve_site_absolute_target("/fc-docs/docs/zh-CN/example.md"),
            check_docs.ROOT / "docs/zh-CN/example.md",
        )
        self.assertIsNone(check_docs.resolve_site_absolute_target("/Makefile"))
        self.assertIsNone(check_docs.resolve_site_absolute_target("/docs/../Makefile"))


if __name__ == "__main__":
    unittest.main()

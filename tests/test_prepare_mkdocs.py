from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "prepare-mkdocs.py"
SPEC = importlib.util.spec_from_file_location("prepare_mkdocs", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load {MODULE_PATH}")
prepare_mkdocs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare_mkdocs)


class PrepareMkDocsTest(unittest.TestCase):
    def test_extract_nav_title(self) -> None:
        text = "---\nnav_title: Short title\n---\n# Long page title\n"
        self.assertEqual(prepare_mkdocs.extract_nav_title(text), "Short title")

    def test_extract_nav_title_accepts_bom_and_crlf(self) -> None:
        text = "\ufeff---\r\nnav_title: Windows title\r\n---\r\n# Long page title\r\n"
        self.assertEqual(prepare_mkdocs.extract_nav_title(text), "Windows title")

    def test_extract_nav_title_requires_closing_delimiter(self) -> None:
        text = "---\nnav_title: Incomplete front matter\n# Long page title\n"
        self.assertIsNone(prepare_mkdocs.extract_nav_title(text))

    def test_clean_label_removes_numeric_prefix(self) -> None:
        self.assertEqual(prepare_mkdocs.clean_label("07.Developer_Reference"), "Developer Reference")

    def test_disambiguate_labels_uses_file_name_fallback(self) -> None:
        labels = [
            ("Error handling", "Error handling"),
            ("Error handling", "Error handling (Python)"),
            ("Overview", "Overview"),
        ]
        self.assertEqual(
            prepare_mkdocs.disambiguate_labels(labels),
            ["Error handling", "Error handling (Python)", "Overview"],
        )

    def test_nav_for_directory_disambiguates_duplicate_h1_titles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            docs_src = Path(directory)
            section = docs_src / "docs"
            section.mkdir()
            (section / "01.Error handling.md").write_text("# Error handling\n", encoding="utf-8")
            (section / "02.Error handling (Python).md").write_text("# Error handling\n", encoding="utf-8")

            original_docs_src = prepare_mkdocs.DOCS_SRC
            prepare_mkdocs.DOCS_SRC = docs_src
            try:
                nav = prepare_mkdocs.nav_for_directory(section)
            finally:
                prepare_mkdocs.DOCS_SRC = original_docs_src

        self.assertEqual(
            [next(iter(item)) for item in nav],
            ["Error handling", "Error handling (Python)"],
        )

    def test_generated_config_enables_pruning_and_anchor_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = Path(directory) / "mkdocs.generated.yml"
            original_config_path = prepare_mkdocs.CONFIG_PATH
            prepare_mkdocs.CONFIG_PATH = config_path
            try:
                prepare_mkdocs.write_config([])
            finally:
                prepare_mkdocs.CONFIG_PATH = original_config_path

            config = config_path.read_text(encoding="utf-8")

        self.assertIn("    - navigation.prune", config)
        self.assertIn("    anchors: warn", config)
        self.assertIn("      enabled: !ENV [CI, false]", config)

    def test_copy_content_requires_every_navigation_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs_src = root / "_mkdocs_src"
            docs_src.mkdir()
            (root / "README.md").write_text("# Home\n", encoding="utf-8")
            (root / "README.en-US.md").write_text("# Home\n", encoding="utf-8")

            original_root = prepare_mkdocs.ROOT
            original_docs_src = prepare_mkdocs.DOCS_SRC
            prepare_mkdocs.ROOT = root
            prepare_mkdocs.DOCS_SRC = docs_src
            try:
                with self.assertRaisesRegex(FileNotFoundError, "CONTRIBUTING.md"):
                    prepare_mkdocs.copy_content()
            finally:
                prepare_mkdocs.ROOT = original_root
                prepare_mkdocs.DOCS_SRC = original_docs_src

    def test_reset_build_dirs_unlinks_external_symlink_without_touching_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "repository"
            outside = base / "outside"
            root.mkdir()
            outside.mkdir()
            marker = outside / "keep.txt"
            marker.write_text("keep", encoding="utf-8")

            docs_src = root / "_mkdocs_src"
            docs_src.symlink_to(outside, target_is_directory=True)
            site_dir = root / "_site"
            site_dir.mkdir()

            original_root = prepare_mkdocs.ROOT
            original_docs_src = prepare_mkdocs.DOCS_SRC
            original_site_dir = prepare_mkdocs.SITE_DIR
            prepare_mkdocs.ROOT = root
            prepare_mkdocs.DOCS_SRC = docs_src
            prepare_mkdocs.SITE_DIR = site_dir
            try:
                prepare_mkdocs.reset_build_dirs()
            finally:
                prepare_mkdocs.ROOT = original_root
                prepare_mkdocs.DOCS_SRC = original_docs_src
                prepare_mkdocs.SITE_DIR = original_site_dir

            self.assertTrue(docs_src.is_dir())
            self.assertFalse(docs_src.is_symlink())
            self.assertTrue(marker.is_file())
            self.assertFalse(site_dir.exists())


if __name__ == "__main__":
    unittest.main()

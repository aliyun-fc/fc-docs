import importlib.util
import pathlib
import sys
import unittest


MODULE = pathlib.Path(__file__).parents[1] / "run.py"
SPEC = importlib.util.spec_from_file_location("desktop_demo", MODULE)
desktop_demo = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = desktop_demo
SPEC.loader.exec_module(desktop_demo)


class ConfigurationTests(unittest.TestCase):
    def test_existing_template_skips_build_requirements(self):
        config = desktop_demo.DemoConfig.from_mapping(
            {
                "E2B_API_KEY": "redacted",
                "E2B_API_URL": "https://api.example.test",
                "E2B_DOMAIN": "example.test",
                "E2B_DESKTOP_TEMPLATE_ID": "tmpl-existing",
            }
        )
        self.assertEqual(config.template_id, "tmpl-existing")
        self.assertIsNone(config.image)

    def test_build_requires_image(self):
        with self.assertRaisesRegex(ValueError, "E2B_DESKTOP_IMAGE"):
            desktop_demo.DemoConfig.from_mapping(
                {
                    "E2B_API_KEY": "redacted",
                    "E2B_API_URL": "https://api.example.test",
                    "E2B_DOMAIN": "example.test",
                    "E2B_DESKTOP_TEMPLATE": "desktop-v0048",
                }
            )

    def test_build_rejects_reserved_template_name(self):
        with self.assertRaisesRegex(ValueError, "reserved desktop-v prefix"):
            desktop_demo.DemoConfig.from_mapping(
                {
                    "E2B_API_KEY": "redacted",
                    "E2B_API_URL": "https://api.example.test",
                    "E2B_DOMAIN": "example.test",
                    "E2B_DESKTOP_IMAGE": "desktop:latest",
                    "E2B_DESKTOP_TEMPLATE": "desktop-v0048",
                }
            )


class StreamUrlTests(unittest.TestCase):
    def test_accepts_https_vnc_path(self):
        desktop_demo.validate_stream_url(
            "https://6080-sbx.example.test/vnc.html?password=redacted"
        )

    def test_rejects_http_and_wrong_path(self):
        with self.assertRaisesRegex(ValueError, "https"):
            desktop_demo.validate_stream_url("http://sbx.example.test/vnc.html")
        with self.assertRaisesRegex(ValueError, "/vnc.html"):
            desktop_demo.validate_stream_url("https://sbx.example.test/other")

    def test_rejects_hostless_https_url(self):
        with self.assertRaisesRegex(ValueError, "host"):
            desktop_demo.validate_stream_url("https:/vnc.html")


if __name__ == "__main__":
    unittest.main()

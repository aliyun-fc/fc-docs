import importlib.util
import os
import pathlib
import sys
import types
import unittest
from unittest.mock import patch


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


class ReportingTests(unittest.TestCase):
    def test_stage_output_redacts_url_query(self):
        line = desktop_demo.stage_message(
            "desktop_stream",
            "ok",
            "https://6080-sbx.example.test/vnc.html?password=secret",
        )
        self.assertIn("[desktop_stream] ok", line)
        self.assertNotIn("password=secret", line)
        self.assertIn("https://6080-sbx.example.test/vnc.html", line)

    def test_stage_output_redacts_url_userinfo(self):
        line = desktop_demo.stage_message(
            "cleanup",
            "failed",
            "https://user:password@cleanup.example.test/vnc.html?token=secret",
        )
        self.assertNotIn("user:password", line)
        self.assertNotIn("token=secret", line)
        self.assertIn("https://cleanup.example.test/vnc.html", line)

    def test_stage_output_redacts_uppercase_url_scheme(self):
        line = desktop_demo.stage_message(
            "cleanup",
            "failed",
            "HTTPS://user:password@cleanup.example.test/vnc.html?token=secret#fragment",
        )
        self.assertNotIn("user:password", line)
        self.assertNotIn("token=secret", line)
        self.assertNotIn("fragment", line)
        self.assertIn("https://cleanup.example.test/vnc.html", line)

    def test_main_reports_failed_runtime_command_and_preserves_error(self):
        class Desktop:
            sandbox_id = "sbx-safe-id"

            def __init__(self):
                self.commands = types.SimpleNamespace(run=self.run)
                self.killed = False

            def run(self, command):
                raise RuntimeError("command channel failed")

            def kill(self):
                self.killed = True

        desktop = Desktop()
        desktop_sdk = types.ModuleType("e2b_desktop")
        desktop_sdk.Sandbox = types.SimpleNamespace(create=lambda **kwargs: desktop)
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        environment = {
            "E2B_API_KEY": "redacted",
            "E2B_API_URL": "https://api.example.test",
            "E2B_DOMAIN": "example.test",
            "E2B_DESKTOP_TEMPLATE_ID": "tmpl-existing",
        }

        with patch.dict(sys.modules, {"dotenv": dotenv, "e2b_desktop": desktop_sdk}):
            with patch.dict(os.environ, environment, clear=True):
                with patch("builtins.print") as print_mock:
                    with self.assertRaisesRegex(RuntimeError, "command channel failed"):
                        desktop_demo.main()

        self.assertTrue(desktop.killed)
        self.assertIn(
            "[runtime_command] failed",
            [call.args[0] for call in print_mock.call_args_list],
        )

    def test_main_preserves_primary_error_and_reports_sanitized_kill_failure(self):
        class Desktop:
            sandbox_id = "sbx-safe-id"

            def __init__(self):
                self.commands = types.SimpleNamespace(run=self.run)

            def run(self, command):
                raise RuntimeError("command channel failed")

            def kill(self):
                raise RuntimeError(
                    "kill failed at https://user:password@cleanup.example.test/vnc.html?token=secret"
                )

        desktop_sdk = types.ModuleType("e2b_desktop")
        desktop_sdk.Sandbox = types.SimpleNamespace(create=lambda **kwargs: Desktop())
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda: None
        environment = {
            "E2B_API_KEY": "redacted",
            "E2B_API_URL": "https://api.example.test",
            "E2B_DOMAIN": "example.test",
            "E2B_DESKTOP_TEMPLATE_ID": "tmpl-existing",
        }

        with patch.dict(sys.modules, {"dotenv": dotenv, "e2b_desktop": desktop_sdk}):
            with patch.dict(os.environ, environment, clear=True):
                with patch("builtins.print") as print_mock:
                    with self.assertRaisesRegex(RuntimeError, "command channel failed"):
                        desktop_demo.main()

        output = [call.args[0] for call in print_mock.call_args_list]
        self.assertIn("[cleanup] failed sandbox_id=sbx-safe-id", output[-1])
        self.assertIn(
            "kill failed at https://cleanup.example.test/vnc.html", output[-1]
        )
        self.assertNotIn("user:password", output[-1])
        self.assertNotIn("token=secret", output[-1])


if __name__ == "__main__":
    unittest.main()

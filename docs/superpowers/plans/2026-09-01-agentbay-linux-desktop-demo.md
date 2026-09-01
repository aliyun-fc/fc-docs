# AgentBay Linux Desktop Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable, safe diagnostic demo that creates an FC E2B Desktop Sandbox following the migration guide.

**Architecture:** `run.py` owns configuration parsing, step-oriented reporting, and resource cleanup. Small pure helpers validate Template selection and stream URLs so unit tests need no cloud credentials. The only networked action is `main()`, which uses the official E2B SDK to build or reuse a Template, create a Sandbox, validate the runtime and Desktop stream, then always destroys the Sandbox it created.

**Tech Stack:** Python 3.10+, `e2b==2.31.0`, `e2b-desktop==2.4.1`, `python-dotenv`, `unittest`.

---

## File structure

- Create: `demo/agentbay-linux-desktop/run.py` — configuration, diagnostics, Template/Sandbox workflow, cleanup.
- Create: `demo/agentbay-linux-desktop/tests/test_run.py` — pure configuration and URL validation tests.
- Create: `demo/agentbay-linux-desktop/requirements.txt` — pinned dependencies.
- Create: `demo/agentbay-linux-desktop/.env.example` — safe environment variable template.
- Create: `demo/agentbay-linux-desktop/README.md` — setup, expected stages, error interpretation, cleanup behavior.

### Task 1: Add test-first configuration and stream validation helpers

**Files:**
- Create: `demo/agentbay-linux-desktop/tests/test_run.py`
- Create: `demo/agentbay-linux-desktop/run.py`

- [ ] **Step 1: Write the failing tests**

```python
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).parents[1] / "run.py"
SPEC = importlib.util.spec_from_file_location("desktop_demo", MODULE)
desktop_demo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(desktop_demo)


class ConfigurationTests(unittest.TestCase):
    def test_existing_template_skips_build_requirements(self):
        config = desktop_demo.DemoConfig.from_mapping({
            "E2B_API_KEY": "redacted",
            "E2B_API_URL": "https://api.example.test",
            "E2B_DOMAIN": "example.test",
            "E2B_DESKTOP_TEMPLATE_ID": "tmpl-existing",
        })
        self.assertEqual(config.template_id, "tmpl-existing")
        self.assertIsNone(config.image)

    def test_build_requires_image_and_non_reserved_template_name(self):
        with self.assertRaisesRegex(ValueError, "E2B_DESKTOP_IMAGE"):
            desktop_demo.DemoConfig.from_mapping({
                "E2B_API_KEY": "redacted",
                "E2B_API_URL": "https://api.example.test",
                "E2B_DOMAIN": "example.test",
                "E2B_DESKTOP_TEMPLATE": "desktop-v0048",
            })


class StreamUrlTests(unittest.TestCase):
    def test_accepts_https_vnc_path(self):
        desktop_demo.validate_stream_url("https://6080-sbx.example.test/vnc.html?password=redacted")

    def test_rejects_http_and_wrong_path(self):
        with self.assertRaisesRegex(ValueError, "https"):
            desktop_demo.validate_stream_url("http://sbx.example.test/vnc.html")
        with self.assertRaisesRegex(ValueError, "/vnc.html"):
            desktop_demo.validate_stream_url("https://sbx.example.test/other")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `cd demo/agentbay-linux-desktop && python -m unittest tests/test_run.py -v`

Expected: FAIL because `run.py` does not exist.

- [ ] **Step 3: Implement the minimum pure helpers**

```python
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
            return cls(values["E2B_API_KEY"], values["E2B_API_URL"], values["E2B_DOMAIN"], template_id, None, None)
        if not image:
            raise ValueError("E2B_DESKTOP_IMAGE is required when E2B_DESKTOP_TEMPLATE_ID is not set")
        if not template_name:
            raise ValueError("E2B_DESKTOP_TEMPLATE is required when E2B_DESKTOP_TEMPLATE_ID is not set")
        if template_name.startswith("desktop-v"):
            raise ValueError("E2B_DESKTOP_TEMPLATE must not use the reserved desktop-v prefix")
        return cls(values["E2B_API_KEY"], values["E2B_API_URL"], values["E2B_DOMAIN"], None, image, template_name)


def validate_stream_url(value: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme != "https":
        raise ValueError("desktop stream URL must use https")
    if parsed.path != "/vnc.html":
        raise ValueError("desktop stream URL path must be /vnc.html")
```

- [ ] **Step 4: Run the tests and confirm they pass**

Run: `cd demo/agentbay-linux-desktop && python -m unittest tests/test_run.py -v`

Expected: `Ran 4 tests` and `OK`.

- [ ] **Step 5: Commit the test seam**

```bash
git add demo/agentbay-linux-desktop/run.py demo/agentbay-linux-desktop/tests/test_run.py
git commit -m "test(agentbay): 覆盖桌面 Demo 配置和流地址校验"
```

### Task 2: Implement the end-to-end diagnostic workflow

**Files:**
- Modify: `demo/agentbay-linux-desktop/run.py`
- Modify: `demo/agentbay-linux-desktop/tests/test_run.py`

- [ ] **Step 1: Add a failing diagnostic-output test**

```python
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
```

- [ ] **Step 2: Run the added test and confirm it fails**

Run: `cd demo/agentbay-linux-desktop && python -m unittest tests/test_run.py -v`

Expected: FAIL because `stage_message` is not defined.

- [ ] **Step 3: Add reporting and workflow implementation**

Add `stage_message()` that parses URLs and removes query strings before printing. Add `main()` with this exact order:

```python
load_dotenv()
config = DemoConfig.from_mapping(os.environ)
report("configuration", "ok", f"template reuse={bool(config.template_id)}")
template_id = config.template_id or build_template(config)
desktop = Sandbox.create(template=template_id, timeout=900)
try:
    result = desktop.commands.run("printf desktop-runtime-ok")
    if result.stdout != "desktop-runtime-ok":
        raise RuntimeError("unexpected command output")
    desktop.stream.start(require_auth=True)
    auth_key = desktop.stream.get_auth_key()
    stream_url = desktop.stream.get_url(auth_key=auth_key)
    validate_stream_url(stream_url)
    screenshot = desktop.screenshot()
    if not screenshot.startswith(b"\x89PNG\r\n\x1a\n"):
        raise RuntimeError("desktop screenshot is not PNG")
finally:
    desktop.stream.stop()
    desktop.kill()
```

`build_template(config)` calls `Template.build(Template().from_image(config.image), name=config.template_name, cpu_count=4, memory_mb=8192, on_build_logs=default_build_logger())` and returns its Template ID. It must report the Template ID but never the API key, auth key, or complete stream URL.

- [ ] **Step 4: Run all unit tests**

Run: `cd demo/agentbay-linux-desktop && python -m unittest tests/test_run.py -v`

Expected: `Ran 5 tests` and `OK`.

- [ ] **Step 5: Commit the workflow**

```bash
git add demo/agentbay-linux-desktop/run.py demo/agentbay-linux-desktop/tests/test_run.py
git commit -m "feat(agentbay): 增加桌面 Sandbox 端到端诊断"
```

### Task 3: Add runnable configuration and operator documentation

**Files:**
- Create: `demo/agentbay-linux-desktop/requirements.txt`
- Create: `demo/agentbay-linux-desktop/.env.example`
- Create: `demo/agentbay-linux-desktop/README.md`

- [ ] **Step 1: Create pinned requirements**

```text
e2b==2.31.0
e2b-desktop==2.4.1
python-dotenv==1.2.2
```

- [ ] **Step 2: Create safe configuration example**

```dotenv
E2B_API_KEY=
E2B_API_URL=https://api.cn-beijing.e2b.fc.aliyuncs.com
E2B_DOMAIN=cn-beijing.e2b.fc.aliyuncs.com
E2B_DESKTOP_IMAGE=fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/desktop:v0.0.48
E2B_DESKTOP_TEMPLATE=custom-desktop-v0048-20260901
# E2B_DESKTOP_TEMPLATE_ID=
```

- [ ] **Step 3: Write README commands and failure interpretation**

Include these commands:

```bash
cd demo/agentbay-linux-desktop
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m unittest tests/test_run.py -v
python run.py
```

Document that `Template.build` failures are control-plane or image-builder failures; `Sandbox.create` failures are runtime provisioning failures; command failures are runtime/envd channel failures; and stream/screenshot failures are desktop runtime failures. Document that the script deletes only the Sandbox it created and never deletes a Template.

- [ ] **Step 4: Run unit tests and documentation link check**

Run: `cd demo/agentbay-linux-desktop && python -m unittest tests/test_run.py -v && cd ../.. && make check-docs`

Expected: unit tests report `OK`; `check-docs` reports all local references are valid.

- [ ] **Step 5: Commit the runnable package**

```bash
git add demo/agentbay-linux-desktop
git commit -m "docs(agentbay): 补充桌面 Demo 运行说明"
```

### Task 4: Execute the real FC E2B end-to-end diagnostic

**Files:**
- No source changes unless the run reveals a reproducible defect.

- [ ] **Step 1: Create a local secret file without committing it**

Run: `cd demo/agentbay-linux-desktop && cp .env.example .env`

Fill `E2B_API_KEY` through the local secret manager or terminal environment. Do not commit `.env` or print it.

- [ ] **Step 2: Run the full diagnostic with a unique Template name**

Run: `cd demo/agentbay-linux-desktop && E2B_DESKTOP_TEMPLATE=custom-desktop-v0048-e2e-$(date +%Y%m%d%H%M%S) python run.py`

Expected success stages: `configuration`, `template_build`, `sandbox_create`, `runtime_command`, `desktop_stream`, `screenshot`, and `cleanup`.

- [ ] **Step 3: Record the result without credentials**

For success, record the sanitized stage output and created Template ID in the PR. For failure, record the stage name, HTTP/error category, and sanitized message; do not record stream query strings or credentials.

- [ ] **Step 4: Commit only source or documentation corrections revealed by the run**

```bash
git add demo/agentbay-linux-desktop
git commit -m "fix(agentbay): 修正桌面 Demo 端到端诊断"
```

Skip this commit when no source changes are required.

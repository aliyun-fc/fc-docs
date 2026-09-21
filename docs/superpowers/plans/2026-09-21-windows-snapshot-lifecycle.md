# Windows Snapshot Lifecycle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend the existing Chinese Windows Computer Use best practice with a complete, directly runnable Template → Sandbox → Snapshot → restored Sandbox → noVNC Python example.

**Architecture:** Keep the current Desktop SDK tutorial unchanged, then append a self-contained Snapshot lifecycle section. Base the embedded script on the verified `01_windows_snapshot_lifecycle.py` demo, preserving readiness probes, disconnected-response recovery, and cleanup while replacing timestamped milestone output with concise progress messages.

**Tech Stack:** Markdown, Python 3.10+, `e2b==2.45.1`, `httpx==0.28.1`, `python-dotenv==1.2.3`, MkDocs Material.

---

### Task 1: Establish the documentation regression check

**Files:**
- Modify: `docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md`
- Reference: `/Users/chenquan/Workspace/fc/fc-sandbox/e2b-demos/e2b-windows-demos/01_windows_snapshot_lifecycle.py`

- [ ] **Step 1: Verify the Snapshot lifecycle section is initially absent**

Run:

```bash
python3 - <<'PY'
from pathlib import Path

path = Path("docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md")
text = path.read_text()
assert "## 使用 Snapshot 保存和恢复 Windows 沙箱" in text
PY
```

Expected: FAIL with `AssertionError`.

- [ ] **Step 2: Confirm the reference script compiles before adapting it**

Run:

```bash
python3 -m py_compile /Users/chenquan/Workspace/fc/fc-sandbox/e2b-demos/e2b-windows-demos/01_windows_snapshot_lifecycle.py
```

Expected: exit code 0.

### Task 2: Add the complete runnable lifecycle example

**Files:**
- Modify: `docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md`

- [ ] **Step 1: Append the lifecycle explanation and prerequisites**

Add the heading `## 使用 Snapshot 保存和恢复 Windows 沙箱`, describe the five lifecycle stages, and state these constraints explicitly:

- Snapshot is allowlisted and only supports second-generation `micro-sandbox` runtime.
- The official Windows image, API key, API URL, domain, and matching-region VPC values are required.
- The example uses 16 vCPU, 16448 MiB memory, and 61440 MiB system disk by default.
- noVNC URLs contain credentials and must not be persisted or shared.

- [ ] **Step 2: Add a complete `.env` example**

Include all required variables with placeholders and optional tuning values with executable defaults:

```dotenv
E2B_API_KEY=<your-api-key>
E2B_API_URL=<your-api-url>
E2B_DOMAIN=<your-domain>
ROOTFS_IMAGE=<official-windows-desktop-image>
E2B_TEMPLATE_SOURCE_VPC_ID=<your-vpc-id>
E2B_TEMPLATE_SOURCE_VSWITCH_IDS=<your-vswitch-id>
E2B_TEMPLATE_SOURCE_SECURITY_GROUP_ID=<your-security-group-id>
E2B_TEMPLATE_CPU_COUNT=16
E2B_TEMPLATE_MEMORY_MB=16448
E2B_TEMPLATE_DISK_SIZE=61440
E2B_REQUEST_TIMEOUT_SECONDS=600
SANDBOX_TIMEOUT_SECONDS=900
TEMPLATE_BUILD_TIMEOUT_SECONDS=3600
NOVNC_READY_TIMEOUT_SECONDS=600
CLEANUP_RESTORED_SANDBOX=false
```

- [ ] **Step 3: Embed the complete Python script**

Copy the complete reference implementation into a `python` fence and make only these bounded adaptations:

- Set the usage line to `uv run windows_snapshot_lifecycle.py`.
- Keep the PEP 723 dependency block so `uv run` installs exact dependencies.
- Load `.env` with `override=True` before constructing SDK configuration.
- Preserve template polling, Sandbox create disconnect recovery, Snapshot 503/disconnect recovery, Windows service readiness, RFB first-frame readiness, noVNC readiness, and `finally` cleanup.
- Replace timestamped `milestone()` output with concise step messages; do not remove error context or final resource IDs.
- Keep placeholders and environment-variable configuration; include no credentials.

- [ ] **Step 4: Add run and cleanup instructions**

Document:

```bash
uv run windows_snapshot_lifecycle.py
```

State that the source sandbox is deleted by default, the restored sandbox remains available by default, and setting `CLEANUP_RESTORED_SANDBOX=true` deletes it at process exit. Link to `../04.功能说明/01.沙箱/12.快照.md` for retention, naming, deletion, and billing constraints.

### Task 3: Verify the embedded artifact and repository

**Files:**
- Verify: `docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md`

- [ ] **Step 1: Re-run the heading assertion**

Run the Task 1 assertion again.

Expected: exit code 0.

- [ ] **Step 2: Extract and compile the embedded lifecycle script**

Use a Python parser that locates the code fence immediately following `将以下代码保存为 \`windows_snapshot_lifecycle.py\`` and writes it to `/tmp/windows_snapshot_lifecycle.py`, then run:

```bash
python3 -m py_compile /tmp/windows_snapshot_lifecycle.py
```

Expected: exit code 0.

- [ ] **Step 3: Verify dependencies and imports in an isolated uv environment**

Run:

```bash
uv run --with e2b==2.45.1 --with httpx==0.28.1 --with python-dotenv==1.2.3 \
  python -c "import e2b, httpx, dotenv; print('imports ok')"
```

Expected: `imports ok`.

- [ ] **Step 4: Run repository checks**

Run:

```bash
make check
```

Expected: unit tests, document checks, and strict MkDocs build all pass.

- [ ] **Step 5: Review the complete diff**

Run:

```bash
git diff --check
git diff --stat origin/main...HEAD
git diff origin/main...HEAD -- "docs/zh-CN/01.云沙箱/05.最佳实践/11.使用 Windows Computer Use Sandbox.md"
```

Confirm that the existing Computer Use tutorial remains intact, all new links resolve, no credentials are present, and the only content change is the Snapshot lifecycle addition.


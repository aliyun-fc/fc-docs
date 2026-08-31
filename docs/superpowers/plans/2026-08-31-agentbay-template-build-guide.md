# AgentBay Linux Desktop Template Build Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add bilingual, public-safe instructions for creating an AgentBay migration desktop Template from the FC `desktop:v0.0.44` image, with an advanced Ubuntu 24.04 custom-image path.

**Architecture:** Keep the existing migration guide as the single entry point. Expand its template section into a recommended FC-image flow and an advanced source-image flow that delegates generic ACR EE and runtime-injection details to the existing custom-image-template guide.

**Tech Stack:** Markdown, Python SDK snippets (`e2b`, `e2b-desktop`), Docker/ACR EE commands

---

### Task 1: Expand the Chinese template guidance

**Files:**
- Modify: `docs/zh-CN/01.云沙箱/04.功能说明/14.迁移/2.AgentBay Linux 桌面迁移指南.md`
- Reference: `docs/zh-CN/01.云沙箱/04.功能说明/02.模板/03.构建自定义镜像模板.md`

- [ ] **Step 1: Preserve the verified default image contract**

Keep `fc-e2b-registry.cn-beijing.cr.aliyuncs.com/runtime/desktop:v0.0.44` and explicitly describe it as the currently documented and verified stable default. Keep the `e2b-desktop==2.4.1` plus `desktop:v0.0.44` 35/35 verification statement.

- [ ] **Step 2: Make the recommended build script reproducible**

Update `build.py` to read `FROM_IMAGE` and `E2B_DESKTOP_TEMPLATE` from the environment, require both values, and create a traceable template name such as `agentbay-desktop-v0044-20260831`. Explain that an existing name can be reused by the service, so every changed image or configuration needs a new name.

- [ ] **Step 3: Add a desktop smoke test**

Add a Python example that creates `e2b_desktop.Sandbox` from `build.template_id`, starts the stream, asserts the URL contains `/vnc.html`, and always stops the stream and kills the sandbox in `finally`.

- [ ] **Step 4: Add the advanced Ubuntu 24.04 path**

Add a compact source layout and Dockerfile skeleton based on `ubuntu:24.04`. The skeleton must install `/bin/bash`, Python, certificates, GNOME/Xvfb, x11vnc, noVNC/websockify, Chrome or Chromium dependencies, fonts, and a non-root user. It must not copy internal certificates or set `/.fce2b/entrypoint`; explain that `Template.build()` builder mode injects FC Sandbox runtime dependencies.

- [ ] **Step 5: Add build, local validation, push, and template conversion commands**

Document `docker buildx build --platform linux/amd64`, local noVNC validation, immutable ACR EE tags, same-region VPC access, and reuse of the existing custom-image-template guide. State that production should pin the Ubuntu digest instead of relying on a mutable tag.

### Task 2: Mirror the content in English

**Files:**
- Modify: `docs/en-US/01.FC Agent Sandbox/04.Features/14.Migration/2.AgentBay Linux Desktop Migration Guide.md`
- Reference: `docs/en-US/01.FC Agent Sandbox/04.Features/02.Templates/03.Build Custom Image Templates.md`

- [ ] **Step 1: Mirror headings and recommendations**

Translate the Chinese template sections without changing image versions, SDK versions, resource sizes, commands, environment variable names, or security constraints.

- [ ] **Step 2: Mirror code blocks exactly where language-neutral**

Keep the Python and shell examples behaviorally identical. Only comments, explanatory prose, and example template names may be localized.

- [ ] **Step 3: Verify relative links**

Link to `../02.Templates/03.Build%20Custom%20Image%20Templates.md` and confirm the resolved file exists.

### Task 3: Validate and commit the documentation

**Files:**
- Test: both migration guide files

- [ ] **Step 1: Run Markdown whitespace validation**

Run: `git diff --check`

Expected: exit code 0 and no output.

- [ ] **Step 2: Run public-content and version checks**

Run searches that assert both guides contain `desktop:v0.0.44`, `e2b-desktop==2.4.1`, `ubuntu:24.04`, and `linux/amd64`; assert neither guide contains an internal Code URL, internal CI variable, embedded API key, or `/.fce2b/entrypoint` instruction.

Expected: all positive counts match in Chinese and English; prohibited-content search returns no match.

- [ ] **Step 3: Validate relative Markdown links**

Run a local script that parses relative Markdown links from both changed files, URL-decodes them, resolves them against each document directory, and fails when a target is missing.

Expected: exit code 0 and both guide paths reported as valid.

- [ ] **Step 4: Review the complete branch diff**

Run: `git diff origin/main...HEAD` and `git status --short --branch`.

Expected: only the approved design, plan, and two migration guides are tracked changes; existing untracked `contexts/` and `htnn-gateway` remain untouched.

- [ ] **Step 5: Commit the implementation**

Commit only the plan and two migration guides with author `辰泉 <cq219740@alibaba-inc.com>`, message `docs(agentbay): add desktop template build guidance`, and trailer `Signed-off-by: Blues AI <bluesai@codex.com>`.

### Task 4: Publish the branch and open a pull request

**Files:**
- No file changes

- [ ] **Step 1: Push the branch**

Run: `git push -u origin docs/agentbay-template-build-guide`.

Expected: the remote branch is created and local upstream is configured.

- [ ] **Step 2: Open the pull request**

Create a GitHub pull request targeting `main`. The title is `docs: add AgentBay desktop template build guidance`. The body summarizes the pinned `desktop:v0.0.44` recommended path, Ubuntu 24.04 advanced path, bilingual parity, and validation commands.

- [ ] **Step 3: Verify the pull request**

Open the returned PR URL or query it through the repository CLI and confirm the source branch, target branch, title, and open state.

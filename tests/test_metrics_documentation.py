"""Tests for the "Metrics no longer claims disk support" documentation update.

This PR corrects documentation that previously claimed FC Agent Sandbox /
E2B-compatible Metrics fully supports disk usage reporting. The corrected
docs state that only CPU and memory metrics are usable, and that disk /
page-cache fields return placeholder values that must not be used for
capacity decisions.

These tests read the actual Markdown files shipped in this repository and
assert on the specific wording introduced or removed by the PR, for both
the English (en-US) and Chinese (zh-CN) documentation trees. Because this
repository has no application code, these are content-regression tests:
they protect against silently reintroducing the previous, inaccurate
claims (e.g. "CPU, memory, and disk") and against losing the new
"placeholder value" caveat during future edits.
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

EN_CLI_QUICKSTART = (
    ROOT
    / "docs/en-US/01.FC Agent Sandbox/01.Getting Started/03.Quickstarts"
    / "02.Use FC Agent Sandbox with the CLI.md"
)
EN_E2B_COMPATIBILITY = (
    ROOT / "docs/en-US/01.FC Agent Sandbox/01.Getting Started" / "05.E2B Compatibility.md"
)
EN_METRICS_FEATURE = (
    ROOT / "docs/en-US/01.FC Agent Sandbox/04.Features/01.Sandbox" / "11.Metrics.md"
)
EN_VIEW_METRICS_CLI = (
    ROOT / "docs/en-US/01.FC Agent Sandbox/04.Features/08.CLI" / "09.View Metrics.md"
)
EN_API_LIST = (
    ROOT
    / "docs/en-US/01.FC Agent Sandbox/07.Developer Reference"
    / "01.E2B SDK-compatible API List.md"
)

ZH_CLI_QUICKSTART = (
    ROOT
    / "docs/zh-CN/01.云沙箱/01.开始使用/03.快速入门"
    / "02.通过 CLI 使用云沙箱.md"
)
ZH_E2B_COMPATIBILITY = ROOT / "docs/zh-CN/01.云沙箱/01.开始使用" / "05.E2B 兼容说明.md"
ZH_METRICS_FEATURE = ROOT / "docs/zh-CN/01.云沙箱/04.功能说明/01.沙箱" / "11.指标.md"
ZH_VIEW_METRICS_CLI = ROOT / "docs/zh-CN/01.云沙箱/04.功能说明/08.命令行工具" / "09.查看指标.md"
ZH_API_LIST = ROOT / "docs/zh-CN/01.云沙箱/07.开发参考" / "01.E2B SDK 兼容 API 清单.md"

ALL_CHANGED_FILES = [
    EN_CLI_QUICKSTART,
    EN_E2B_COMPATIBILITY,
    EN_METRICS_FEATURE,
    EN_VIEW_METRICS_CLI,
    EN_API_LIST,
    ZH_CLI_QUICKSTART,
    ZH_E2B_COMPATIBILITY,
    ZH_METRICS_FEATURE,
    ZH_VIEW_METRICS_CLI,
    ZH_API_LIST,
]


def read(path: Path) -> str:
    assert path.is_file(), f"expected doc file to exist: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Sanity: all files touched by the PR exist and are non-empty UTF-8 text.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", ALL_CHANGED_FILES, ids=lambda p: p.name)
def test_changed_file_exists_and_is_non_empty(path: Path) -> None:
    content = read(path)
    assert content.strip(), f"{path} should not be empty"


# ---------------------------------------------------------------------------
# 1. English CLI quickstart: "02.Use FC Agent Sandbox with the CLI.md"
# ---------------------------------------------------------------------------


def test_en_cli_quickstart_mentions_cpu_and_memory_only() -> None:
    content = read(EN_CLI_QUICKSTART)
    assert "View CPU and memory metrics for a running sandbox:" in content


def test_en_cli_quickstart_no_longer_claims_disk_metrics() -> None:
    content = read(EN_CLI_QUICKSTART)
    assert "View CPU, memory, and disk metrics" not in content


# ---------------------------------------------------------------------------
# 2. English E2B Compatibility page
# ---------------------------------------------------------------------------


def test_en_compat_metrics_table_row_updated() -> None:
    content = read(EN_E2B_COMPATIBILITY)
    assert (
        "| Metrics | Compatible | Supports viewing CPU and memory metrics. "
        "Disk and page-cache fields return placeholder values and are not "
        "currently usable. |"
    ) in content


def test_en_compat_metrics_table_row_no_longer_claims_disk_support() -> None:
    content = read(EN_E2B_COMPATIBILITY)
    assert "Supports CPU, memory, disk, and related metrics." not in content


def test_en_compat_cli_metrics_command_row_updated() -> None:
    content = read(EN_E2B_COMPATIBILITY)
    assert (
        "| `sandbox metrics` | Supported | Shows CPU and memory metrics for "
        "a running sandbox. Metrics currently return at 1-minute "
        "granularity. |"
    ) in content


def test_en_compat_cli_metrics_command_row_no_longer_claims_disk_support() -> None:
    content = read(EN_E2B_COMPATIBILITY)
    assert "Shows CPU, memory, disk, and related metrics" not in content


def test_en_compat_metrics_section_paragraph_updated() -> None:
    content = read(EN_E2B_COMPATIBILITY)
    assert (
        "Currently supports CPU and memory metrics. Disk and page-cache "
        "fields return placeholder values and should not be used for "
        "capacity decisions."
    ) in content
    # The rest of the original guidance sentence must be preserved.
    assert (
        "Metrics currently return at 1-minute granularity. They are "
        "suitable for debugging, resource trend observation, and task "
        "troubleshooting."
    ) in content


# ---------------------------------------------------------------------------
# 3. English Sandbox Metrics feature page
# ---------------------------------------------------------------------------


def test_en_metrics_feature_intro_mentions_cpu_and_memory_only() -> None:
    content = read(EN_METRICS_FEATURE)
    assert (
        "Sandbox Metrics lets you inspect runtime metrics such as CPU and "
        "memory. FC Agent Sandbox supports sandbox metrics and currently "
        "returns data at 1-minute granularity."
    ) in content


def test_en_metrics_feature_intro_no_longer_mentions_disk_usage() -> None:
    content = read(EN_METRICS_FEATURE)
    assert "such as CPU, memory, and disk usage" not in content


def test_en_metrics_feature_response_description_updated() -> None:
    content = read(EN_METRICS_FEATURE)
    assert (
        "The response includes the sampling time, CPU usage and core "
        "count, and memory used and total. Disk and page-cache fields "
        "return placeholder values and should not be used for capacity "
        "decisions."
    ) in content


def test_en_metrics_feature_response_description_no_longer_claims_disk_total() -> None:
    content = read(EN_METRICS_FEATURE)
    assert "and disk used and total" not in content


def test_en_metrics_feature_still_has_sdk_and_cli_examples() -> None:
    # Guard against accidental removal of unrelated content while editing
    # the surrounding prose.
    content = read(EN_METRICS_FEATURE)
    assert "sandbox.getMetrics()" in content
    assert "sandbox.get_metrics()" in content
    assert "e2b sandbox metrics <sandbox-id>" in content


# ---------------------------------------------------------------------------
# 4. English "View Metrics" CLI feature page
# ---------------------------------------------------------------------------


def test_en_view_metrics_cli_output_description_updated() -> None:
    content = read(EN_VIEW_METRICS_CLI)
    assert (
        "The output includes CPU and memory metrics. Disk fields appear as "
        "placeholder values. For example:"
    ) in content


def test_en_view_metrics_cli_no_longer_claims_full_disk_metrics() -> None:
    content = read(EN_VIEW_METRICS_CLI)
    assert "The output includes CPU, memory, and disk metrics." not in content


def test_en_view_metrics_cli_example_output_unchanged() -> None:
    # The example transcript itself (with Disk: 0 / 0 MiB placeholders) is
    # untouched by this PR and should still be present verbatim.
    content = read(EN_VIEW_METRICS_CLI)
    assert "Disk:     0 / 0     MiB" in content


# ---------------------------------------------------------------------------
# 5. English E2B SDK-compatible API List (Developer Reference)
# ---------------------------------------------------------------------------


def test_en_api_list_metrics_paragraph_updated() -> None:
    content = read(EN_API_LIST)
    assert (
        "Sandbox Metrics currently supports viewing CPU and memory "
        "metrics. Disk and page-cache fields return placeholder values and "
        "should not be used for capacity decisions. Metrics return at "
        "1-minute granularity."
    ) in content


def test_en_api_list_metrics_paragraph_no_longer_claims_disk_support() -> None:
    content = read(EN_API_LIST)
    assert (
        "Sandbox Metrics currently supports CPU, memory, disk, and related "
        "metrics at 1-minute granularity."
    ) not in content


# ---------------------------------------------------------------------------
# 6. Chinese CLI quickstart: "02.通过 CLI 使用云沙箱.md"
# ---------------------------------------------------------------------------


def test_zh_cli_quickstart_mentions_cpu_and_memory_only() -> None:
    content = read(ZH_CLI_QUICKSTART)
    assert "查看运行中 Sandbox 的 CPU、内存指标：" in content


def test_zh_cli_quickstart_no_longer_claims_disk_metrics() -> None:
    content = read(ZH_CLI_QUICKSTART)
    assert "CPU、内存和磁盘指标" not in content


# ---------------------------------------------------------------------------
# 7. Chinese E2B Compatibility page
# ---------------------------------------------------------------------------


def test_zh_compat_metrics_table_row_updated() -> None:
    content = read(ZH_E2B_COMPATIBILITY)
    assert (
        "| Metrics | 兼容 | 支持查看 CPU、内存指标；磁盘/页缓存字段会返回占位值，暂不可用。 |"
        in content
    )


def test_zh_compat_metrics_table_row_no_longer_says_unsupported() -> None:
    content = read(ZH_E2B_COMPATIBILITY)
    # The previous wording said the fields were simply "not supported"
    # rather than clarifying they return placeholder values.
    assert "磁盘/页缓存字段暂不支持。" not in content


def test_zh_compat_metrics_section_paragraph_updated() -> None:
    content = read(ZH_E2B_COMPATIBILITY)
    assert (
        "当前支持 CPU、内存指标；磁盘/页缓存字段会返回占位值，不建议用于容量判断。"
        in content
    )


def test_zh_compat_metrics_section_paragraph_no_longer_says_unsupported() -> None:
    content = read(ZH_E2B_COMPATIBILITY)
    assert "当前支持 CPU、内存指标，磁盘/页缓存字段暂不支持。" not in content


# ---------------------------------------------------------------------------
# 8. Chinese Sandbox Metrics feature page ("11.指标.md")
# ---------------------------------------------------------------------------


def test_zh_metrics_feature_intro_mentions_cpu_and_memory_only() -> None:
    content = read(ZH_METRICS_FEATURE)
    assert "Sandbox Metrics 用于查询 CPU、内存等运行指标。" in content


def test_zh_metrics_feature_intro_no_longer_mentions_disk() -> None:
    content = read(ZH_METRICS_FEATURE)
    assert "CPU、内存、磁盘等运行指标" not in content


def test_zh_metrics_feature_response_description_updated() -> None:
    content = read(ZH_METRICS_FEATURE)
    assert (
        "返回内容包含采样时间、CPU 使用率和核数、内存使用量和总量。"
        "磁盘和页缓存字段会返回占位值，不建议用于容量判断。"
    ) in content


def test_zh_metrics_feature_response_description_no_longer_claims_disk_total() -> None:
    content = read(ZH_METRICS_FEATURE)
    assert "磁盘使用量和总量" not in content


def test_zh_metrics_feature_still_has_sdk_and_cli_examples() -> None:
    content = read(ZH_METRICS_FEATURE)
    assert "sandbox.getMetrics()" in content
    assert "sandbox.get_metrics()" in content
    assert "e2b sandbox metrics <sandbox-id>" in content


# ---------------------------------------------------------------------------
# 9. Chinese "查看指标" CLI feature page
# ---------------------------------------------------------------------------


def test_zh_view_metrics_cli_output_description_updated() -> None:
    content = read(ZH_VIEW_METRICS_CLI)
    assert "输出包含 CPU、内存指标；磁盘字段会显示为占位值。例如：" in content


def test_zh_view_metrics_cli_no_longer_claims_full_disk_metrics() -> None:
    content = read(ZH_VIEW_METRICS_CLI)
    assert "输出包含 CPU、内存和磁盘指标。" not in content


def test_zh_view_metrics_cli_example_output_unchanged() -> None:
    content = read(ZH_VIEW_METRICS_CLI)
    assert "Disk:     0 / 0     MiB" in content


# ---------------------------------------------------------------------------
# 10. Chinese E2B SDK 兼容 API 清单 (Developer Reference)
# ---------------------------------------------------------------------------


def test_zh_api_list_metrics_paragraph_updated() -> None:
    content = read(ZH_API_LIST)
    assert (
        "Sandbox Metrics 当前支持查看 CPU、内存指标；磁盘/页缓存字段会返回占位值，"
        "不建议用于容量判断。指标按 1 分钟粒度返回。"
    ) in content


def test_zh_api_list_metrics_paragraph_no_longer_claims_disk_support() -> None:
    content = read(ZH_API_LIST)
    assert "Sandbox Metrics 当前支持查看 CPU、内存、磁盘等指标" not in content


# ---------------------------------------------------------------------------
# Cross-cutting regression checks
# ---------------------------------------------------------------------------


# Phrases that claimed (or implied) full disk-metrics support before this
# PR. None of these should reappear in any of the ten files touched by the
# PR; if they do, the inaccurate claim has been reintroduced.
FORBIDDEN_PHRASES = [
    "View CPU, memory, and disk metrics",
    "Supports CPU, memory, disk, and related metrics",
    "Shows CPU, memory, disk, and related metrics",
    "such as CPU, memory, and disk usage",
    "and disk used and total",
    "The output includes CPU, memory, and disk metrics.",
    "Sandbox Metrics currently supports CPU, memory, disk, and related metrics",
    "CPU、内存和磁盘指标",
    "CPU、内存、磁盘等运行指标",
    "磁盘使用量和总量",
    "输出包含 CPU、内存和磁盘指标。",
    "Sandbox Metrics 当前支持查看 CPU、内存、磁盘等指标",
]


@pytest.mark.parametrize("path", ALL_CHANGED_FILES, ids=lambda p: p.name)
def test_no_file_reintroduces_full_disk_metrics_claim(path: Path) -> None:
    content = read(path)
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in content, (
            f"{path} unexpectedly contains outdated wording: {phrase!r}"
        )


@pytest.mark.parametrize(
    "path",
    [
        EN_E2B_COMPATIBILITY,
        EN_METRICS_FEATURE,
        EN_VIEW_METRICS_CLI,
        EN_API_LIST,
        ZH_E2B_COMPATIBILITY,
        ZH_METRICS_FEATURE,
        ZH_VIEW_METRICS_CLI,
        ZH_API_LIST,
    ],
    ids=lambda p: p.name,
)
def test_metrics_pages_document_disk_as_placeholder_not_supported(path: Path) -> None:
    """Every page that discusses disk metrics must flag them as a
    placeholder/unusable value rather than silently omitting the caveat."""
    content = read(path)
    has_placeholder_note = (
        "placeholder value" in content
        or "占位值" in content
        or "appear as placeholder values" in content
        or "显示为占位值" in content
    )
    assert has_placeholder_note, (
        f"{path} should clarify that disk/page-cache metrics are "
        "placeholder values"
    )


def test_en_and_zh_metrics_feature_pages_are_semantically_aligned() -> None:
    """The English and Chinese versions of the Sandbox Metrics feature page
    should agree on the core fact: only CPU and memory are usable, disk and
    page-cache are placeholders."""
    en_content = read(EN_METRICS_FEATURE)
    zh_content = read(ZH_METRICS_FEATURE)

    assert "CPU and memory" in en_content
    assert "CPU、内存" in zh_content

    assert "Disk and page-cache fields return placeholder values" in en_content
    assert "磁盘和页缓存字段会返回占位值" in zh_content


def test_en_and_zh_cli_quickstart_pages_are_semantically_aligned() -> None:
    en_content = read(EN_CLI_QUICKSTART)
    zh_content = read(ZH_CLI_QUICKSTART)

    assert "View CPU and memory metrics for a running sandbox:" in en_content
    assert "查看运行中 Sandbox 的 CPU、内存指标：" in zh_content

    # Neither language should mention disk in the sandbox-metrics step.
    assert "disk" not in en_content.split("## 7. View sandbox metrics")[1].split(
        "## 8."
    )[0].lower()
    assert "磁盘" not in zh_content.split("## 7. 查看 Sandbox 指标")[1].split("## 8.")[0]
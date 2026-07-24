# Contributing Guide

Thank you for improving the Alibaba Cloud Function Compute documentation. This guide explains how to preview the site, run checks, and submit changes.

## Set Up the Environment

The repository uses Python 3.12, MkDocs Material, and Make. Install the dependencies:

```bash
make install
```

## Preview the Site

Start the local development server:

```bash
make serve
```

The build script generates temporary MkDocs source and configuration files from `docs/`, `assets/`, and the root README files. Do not edit `_mkdocs_src/`, `_site/`, or `mkdocs.generated.yml` manually.

## Run Checks

Run the script tests, documentation checks, and strict site build:

```bash
make check
```

Pull request CI runs the same command. Any MkDocs warning fails the check.

The checks cover heading structure, local references, path whitespace, asset size, and the MkDocs build.

## Edit Documentation

- Put Chinese pages in `docs/zh-CN/` and English pages in `docs/en-US/`.
- Put localized images and media in `assets/zh-CN/` or `assets/en-US/`.
- Follow the numeric prefixes and naming conventions used by neighboring files.
- Use one H1 per page and increase heading levels one level at a time.
- Use relative links for repository documents and assets.
- Never commit real AccessKeys, API keys, tokens, or other credentials.
- Put generated API Reference content only in an `API Reference/` directory under the relevant developer-reference section.

To set a shorter navigation label, add `nav_title` to the page front matter:

```yaml
---
nav_title: Short navigation title
---
```

## Submit a Pull Request

Describe the scope, reason, and validation results. Commit new or replacement media with the page that references it, and confirm that `make check` passes.

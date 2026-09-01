# AgentBay Linux Desktop end-to-end demo design

## Goal

Provide a standalone, reproducible demo at `demo/agentbay-linux-desktop/` that follows the AgentBay Linux Desktop migration guide to build or reuse a Template, create a Sandbox, and verify Desktop SDK and noVNC stream access.

## Scope

The demo contains:

- `run.py`: a single command-line entry point.
- `requirements.txt`: pinned official SDK versions, `e2b==2.31.0` and `e2b-desktop==2.4.1`.
- `.env.example`: non-secret configuration placeholders.
- `README.md`: prerequisites, setup, commands, expected stages, and cleanup behavior.

It does not publish images, modify an existing Template, or expose credentials.

## Interface and configuration

`python run.py` reads environment variables through `.env` or the process environment.

| Variable | Required | Purpose |
| --- | --- | --- |
| `E2B_API_KEY` | yes | API Key for the configured FC E2B region. |
| `E2B_API_URL` | yes | FC E2B control-plane endpoint. |
| `E2B_DOMAIN` | yes | FC E2B data-plane domain. |
| `E2B_DESKTOP_IMAGE` | build path | Source image; defaults to FC Desktop `v0.0.48`. |
| `E2B_DESKTOP_TEMPLATE` | build path | New, non-reserved Template name. |
| `E2B_DESKTOP_TEMPLATE_ID` | reuse path | Existing Template ID; skips the build step. |

At least one of `E2B_DESKTOP_TEMPLATE_ID` or the build-path variables must be supplied. The Template name must not use the reserved `desktop-v*` prefix.

## Flow

1. Validate local configuration without printing secret values.
2. Confirm control-plane reachability.
3. Build a Template from `E2B_DESKTOP_IMAGE`, or use `E2B_DESKTOP_TEMPLATE_ID`.
4. Create a Sandbox from the selected Template.
5. Execute a simple command through the SDK to validate the runtime channel.
6. Start an authenticated Desktop stream, retrieve the temporary auth key, and validate that the URL is HTTPS with exact path `/vnc.html`.
7. Capture a PNG screenshot and validate its header.
8. Stop the stream and destroy the Sandbox in `finally`.

## Diagnostics and safety

Each step emits one structured, human-readable stage result. Failures identify the failing layer: configuration, control plane, Template build, Sandbox creation, command channel, desktop stream, or screenshot. Output must not include API Keys, auth keys, request headers, or query strings from stream URLs.

The demo always destroys the Sandbox it created. It does not delete Templates because Templates may be intentionally reused. The exit code is non-zero on a failed stage.

## Verification seams

- Configuration seam: required variables and mutually exclusive Template selection are accepted or rejected before a network call.
- Stream seam: an authenticated stream produces a non-empty temporary key and an HTTPS `/vnc.html` URL.
- End-to-end seam: with a valid configured Template, Sandbox creation, command execution, stream setup, and PNG screenshot all succeed, then the Sandbox is removed.

## Testing plan

Unit tests cover configuration selection and stream URL validation without credentials. The end-to-end command uses the configured FC E2B account and verifies the full flow against a real Desktop Template.

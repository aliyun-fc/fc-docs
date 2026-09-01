# AgentBay Linux Desktop diagnostic demo

This demo builds or reuses an FC E2B Desktop Template, creates a Desktop
Sandbox, and verifies its command channel, authenticated noVNC stream, and
PNG screenshot. It is an operator diagnostic: do not run it until the API key
and region endpoints are configured for an account you are authorized to use.

## Setup and run

Use Python 3. The local system does not provide a `python` command, so use
`python3` throughout.

```bash
cd demo/agentbay-linux-desktop
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` locally and set `E2B_API_KEY`. Never commit `.env` or paste the key
into terminal logs, tickets, or chat. The example selects the Desktop image
`v0.0.48` and a non-reserved Template name. Change
`E2B_DESKTOP_TEMPLATE` to a unique name when building a Template. Names that
start with `desktop-v` are reserved. Alternatively, set
`E2B_DESKTOP_TEMPLATE_ID` to reuse an existing Template; this skips the image
build and makes the image and Template-name values unnecessary.

Run the offline unit tests before the diagnostic:

```bash
python3 -m unittest tests/test_run.py -v
```

Run the cloud diagnostic only after local configuration is complete:

```bash
python3 run.py
```

## Expected stages and diagnostics

On success, the script reports these stages in order:

1. `configuration` validates local settings without displaying secrets.
2. `template_build` builds the image, unless a Template ID is reused.
3. `sandbox_create` provisions the Desktop Sandbox.
4. `runtime_command` verifies the runtime command/envd channel.
5. `desktop_stream` starts an authenticated HTTPS `/vnc.html` stream.
6. `screenshot` validates a PNG screenshot.
7. `cleanup` stops the stream and destroys the Sandbox.

Use the failing stage to locate the layer to investigate:

| Stage | Likely layer |
| --- | --- |
| `template_build` | Control plane or image-builder failure. |
| `sandbox_create` | Runtime provisioning failure. |
| `runtime_command` | Runtime or envd command-channel failure. |
| `desktop_stream` or `screenshot` | Desktop runtime failure. |

`configuration` errors are local input problems (for example, a missing API
key, endpoint, or invalid Template selection). A failure is re-raised with a
non-zero exit code after the stage report.

## Resource cleanup and secret safety

The script always attempts cleanup in `finally`: it stops a stream it started
and deletes only the Sandbox created by that invocation. It never deletes a
Template, including one it just built, because Templates can be reused.

The diagnostic output intentionally omits API keys, temporary stream auth
keys, and URL query strings. Keep that boundary when collecting failure
evidence: record the stage and sanitized error category, never credentials,
request headers, or complete authenticated stream URLs.

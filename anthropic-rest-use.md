# Using Claude Code for one-shot completions (on your subscription)

This note documents how to get **single-shot LLM completions** out of the `claude` CLI —
the approach used by `scripts/analyze_documents_claude.py` to evaluate PNCP contracts.

## Why the CLI, not the REST API

We want completions billed to the **Claude Pro/Max subscription**, not a metered
`ANTHROPIC_API_KEY`. The relevant facts:

- The subscription OAuth token (`sk-ant-oat01-…`, from `claude setup-token`) is **rejected
  by the raw `/v1/messages` REST endpoint** ("OAuth authentication is currently not
  supported"), and using it elsewhere violates Anthropic's ToS. So you cannot point the
  standard `anthropic` SDK at `api.anthropic.com` with subscription credentials.
- The **supported** path to spend the subscription programmatically is the `claude` CLI
  (or the Claude Agent SDK), which authenticates with your logged-in session and counts
  usage against the plan (plus **usage credits** when you exceed the plan limits —
  enabled in Settings → Usage).

So: run `claude -p` headless for one-shot completions. Same model, same wire format under
the hood, billed to the subscription.

## The one-shot pattern

```bash
echo "<your prompt>" | claude -p \
  --model claude-sonnet-4-6 \
  --output-format json \
  --append-system-prompt "Answer with valid JSON only, no markdown." \
  --max-turns 1 \
  --allowedTools ""
```

Flags that matter:

| Flag | Purpose |
|---|---|
| `-p` / `--print` | Headless: print the response and exit (no interactive session). |
| `--output-format json` | Wrap the answer in a JSON envelope with usage/cost metadata. |
| `--append-system-prompt` | Add instructions on top of the default system prompt. |
| `--max-turns 1` | Force a single turn — no agentic loop. |
| `--allowedTools ""` | Disable tools, so it's a pure completion (no Bash/Read/etc.). |
| `--model <id>` | e.g. `claude-sonnet-4-6`, `claude-opus-4-8`, `claude-haiku-4-5`. |

Pass the prompt on **stdin** (as above) rather than as an argument when it contains large
JSON or document text — it avoids shell-escaping problems.

## The JSON envelope

With `--output-format json` you get an object like:

```json
{
  "type": "result",
  "is_error": false,
  "stop_reason": "end_turn",
  "result": "{\"ok\": true}",          // <- the model's actual answer (a string)
  "total_cost_usd": 0.0337,
  "duration_ms": 10877,
  "usage": {
    "input_tokens": 3,
    "output_tokens": 417,
    "cache_creation_input_tokens": 9996,
    "cache_read_input_tokens": 16758,
    "service_tier": "standard"
  },
  "model_usage": { ... },
  "session_id": "...",
  "uuid": "..."
}
```

Key fields:
- **`result`** — the model's reply as a **string**. If you asked for JSON, parse this
  string a second time. Check `is_error` first.
- **`total_cost_usd`** / **`usage`** — per-call cost and token accounting. Sum these across
  a batch to size a full run before committing usage.
- **`stop_reason`** — `end_turn` for a normal completion.

## Python: structured one-shot

This is the exact shape used in `scripts/analyze_documents_claude.py` (`call_claude`):

```python
import json
import subprocess

SYSTEM_PROMPT = "Answer with a single valid JSON object only. No markdown, no prose."

def one_shot_json(prompt: str, model: str = "claude-sonnet-4-6") -> dict:
    proc = subprocess.run(
        ["claude", "-p",
         "--model", model,
         "--output-format", "json",
         "--append-system-prompt", SYSTEM_PROMPT,
         "--max-turns", "1",
         "--allowedTools", ""],
        input=prompt,            # prompt via stdin
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:400]}")

    envelope = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude CLI is_error: {envelope.get('result')!r}")

    answer = json.loads(strip_fences(envelope["result"]))   # model's JSON
    return {"answer": answer, "usage": envelope.get("usage"),
            "cost_usd": envelope.get("total_cost_usd")}

def strip_fences(text: str) -> str:
    """Remove ```json fences if the model wraps its output."""
    import re
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*\n?", "", s)
        s = re.sub(r"\n?```$", "", s.strip())
    return s.strip()
```

Defensive notes (learned in this project):
- Models sometimes wrap JSON in ```` ```json ```` fences even when told not to — strip them.
- Catch `json.JSONDecodeError` and keep the raw `result` for debugging instead of aborting
  a whole batch (the script records a `parse_error` status per row).
- Add a small `time.sleep()` between calls in a loop; track `total_cost_usd` per call.

## Plain text instead of JSON

Drop `--output-format json` (or use `--output-format text`) and the CLI prints the raw
completion straight to stdout — convenient for quick shell use:

```bash
echo "Summarize this in one sentence: ..." | claude -p --model claude-haiku-4-5 --max-turns 1
```

## Caveats

- **One-shot only.** `--max-turns 1` + `--allowedTools ""` keeps it a pure completion. Drop
  those if you actually want the agentic loop / tool use.
- **Subscription, not REST.** This bills the logged-in plan. For raw `/v1/messages` access
  you still need a Console `ANTHROPIC_API_KEY` (separate billing).
- **Auth precedence.** If `ANTHROPIC_API_KEY` is set in the environment, the CLI uses it
  (metered) instead of the subscription. `unset ANTHROPIC_API_KEY` to force subscription
  usage.
- **Cost.** In this project each evaluation call ran ~US$ 0.066 on `claude-sonnet-4-6`
  (~10k input + ~400 output tokens). Measure with `total_cost_usd` before scaling up.

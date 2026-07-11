---
name: tokenfactory
description: >-
  Use Nebius Token Factory for LLM inference in the Emergence × Nebius Enterprise
  Agent Hackathon. Covers first-time setup (getting an API key/credits, storing
  the key securely in the shell), the OpenAI-compatible endpoint, picking a model
  (Nemotron-3 Super 120B default), function/tool calling to drive CRAFT MCP tools,
  streaming, batch, embeddings, LiteLLM/LangChain/LangGraph wiring, installing the
  claude-codex-nebius-proxy to route Claude Code or the Codex CLI, and
  troubleshooting. Trigger whenever a
  user is new to Token Factory, needs an API key set up, needs to call an LLM,
  configure inference, pick a model, do function calling, wire up Claude Code or
  Codex, or connect a reasoning model to the CRAFT data platform.
---

# Nebius Token Factory — Skill

Token Factory is Nebius's managed inference platform. It serves open models behind an
**OpenAI-compatible API**, so any agent framework that speaks OpenAI (or has a Nebius/OpenAI
provider) can use it by changing three things: **base URL**, **API key**, and **model name**.

In this hackathon, the pattern is:

> **CRAFT (over MCP) handles data retrieval → your model on Token Factory does the reasoning and tool-calling.**

Your agent calls a Token Factory model; the model emits **tool calls**; your code dispatches
those to **CRAFT's MCP tools** (`get_schema`, `generate_sql`, `execute_query`,
`generate_plotly_chart`, …) and feeds results back. See `reference/craft-integration.md`.

## 1. Get access (do this first)

New to Token Factory? It's three steps: **get a key → store it securely → make one test call.**
If the user doesn't have a key yet, walk them through this section before anything else.

1. Claim credits at **https://dev.nebius.com/builders** (apply early — approval can lag).
2. Log in to the Token Factory dashboard and create/copy your **API key**.
3. Store it as an environment variable — **never hardcode it in source code, never commit it**:

   ```bash
   # Add an environment variable for your API key to store it locally.
   # Copy-paste this into your terminal and insert your API key:
   export NEBIUS_API_KEY="your-key-here"
   export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"

   # Persist across sessions:
   echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.zshrc    # macOS (default shell: zsh)
   echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.bashrc   # Linux (bash)
   # Then open a new terminal, or reload now: source ~/.zshrc  (or: source ~/.bashrc)
   ```

   Per-project alternative: `cp .env.example .env` and fill in the key — `.env` is gitignored here.

4. Verify it works (should print a JSON list of models):

   ```bash
   curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY" | head
   ```

   If it errors, see `reference/troubleshooting.md` (401 = key/credits issue, connection error = base URL).

**Key safety:** treat the key like a password. Don't paste it into chats, issues, or shared docs;
don't commit it (this repo's `.gitignore` already excludes `.env`); if it leaks, revoke it in the
dashboard and create a new one.

> If a helper wants `OPENAI_API_KEY` / `OPENAI_BASE_URL` (many do), set those to the Nebius values.

## 2. First call (OpenAI SDK)

```python
from openai import OpenAI
import os

client = OpenAI(
    base_url=os.environ["NEBIUS_BASE_URL"],
    api_key=os.environ["NEBIUS_API_KEY"],
)

resp = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",   # recommended for agentic tool use
    messages=[{"role": "user", "content": "Say hello in one sentence."}],
)
print(resp.choices[0].message.content)
```

That's the whole integration surface. Everything else — streaming, tools, batch,
embeddings — is standard OpenAI-shaped and documented in `reference/api.md`.

## 3. Which model?

**New to this? Don't agonize — use the default below and move on; you can switch any time**
(it's just the `model` string). To see everything available on your account:
`curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY"`.

- **Default for agents / tool use:** `nvidia/nemotron-3-super-120b-a12b`
  (Nemotron-3 Super 120B, ~12B active, 1M context, **native function calling**).
- Token Factory hosts many open models (Llama, Qwen, DeepSeek, Kimi, etc.). Pick the smallest
  model that reliably tool-calls for your loop; scale up only if reasoning quality needs it.
- Full guidance + model IDs: `reference/models.md`.

## 4. Function calling → CRAFT

The whole game is: model proposes a tool call → you run the CRAFT MCP tool → return the result.
Minimal loop and a full LangGraph example: `reference/function-calling.md` and
`examples/function_calling_craft.py`.

## 5. Identify the user's stack, then wire it

Before giving setup instructions, figure out which of these the user is on — ask if it isn't
obvious from context ("Are you writing your own agent in Python/JS, or using Claude Code or
the Codex CLI?"). The setup differs:

| Stack | Wiring |
|---|---|
| **Own agent — OpenAI SDK (Python/JS)** | No proxy needed. Set `base_url` + `api_key` from the env vars in §1 (snippet in §2). |
| **Own agent — LiteLLM** | `model="nebius/nvidia/nemotron-3-super-120b-a12b"`, reads `NEBIUS_API_KEY` from env. |
| **Own agent — LangChain / LangGraph** | `ChatOpenAI(base_url=..., api_key=..., model=...)`. |
| **Claude Code** | Claude Code speaks Anthropic's `/v1/messages`, not OpenAI — route through a local proxy. Install walkthrough: `reference/proxy-setup.md`; quick reference: `reference/api.md` → "CLI routing". |
| **Codex CLI** | Same proxy, plus `~/.codex/config.toml` with `wire_api = "responses"`. Install walkthrough: `reference/proxy-setup.md`. |

**Secure key handling on every path:** the key lives in the `NEBIUS_API_KEY` environment
variable (§1). CLI configs should reference it via `env_key` (Codex) or the proxy's environment —
never paste the raw key into a config file, script, or repo.

Copy-paste snippets for each: `reference/api.md`. Runnable examples: `examples/`.

## 6. When stuck

`reference/troubleshooting.md` covers auth/401, wrong base URL, model-not-found,
rate limits, tool-call JSON issues, and context-length errors.

## Reference map

| File | What's in it |
|------|--------------|
| `reference/api.md` | Endpoints, auth, streaming, curl/Python/JS, LiteLLM, LangChain, CLI routing |
| `reference/models.md` | Recommended models, IDs, when to use which |
| `reference/function-calling.md` | Tool-calling loop, schema format, dispatching to CRAFT MCP |
| `reference/batch-and-embeddings.md` | Batch API (evals) and embeddings (RAG over schema docs) |
| `reference/craft-integration.md` | The CRAFT-over-MCP + Token Factory architecture, end to end |
| `reference/proxy-setup.md` | Install claude-codex-nebius-proxy: TUI installer, Claude Code + Codex wiring |
| `reference/troubleshooting.md` | Common errors and fixes |
| `examples/` | Runnable Python: quickstart, LiteLLM, function calling, LangGraph+CRAFT |

## Related resources

- **Token Factory Cookbook** — 50 recipes / 27 notebooks: https://github.com/nebius/token-factory-cookbook
- **Ecosystem cookbook mirror** — https://github.com/opencolin/nebius-ecosystem-cookbook
- **awesome-nebius** — curated Nebius resources: https://github.com/opencolin/awesome-nebius
- **Claude Code / Codex → Nebius proxy** — https://github.com/opencolin/claude-codex-nebius-proxy
- **openclaw-nebius-plugin** — https://github.com/opencolin/openclaw-nebius-plugin

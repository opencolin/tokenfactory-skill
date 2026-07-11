---
name: tokenfactory
description: >-
  Use Nebius Token Factory for LLM inference in the Emergence × Nebius Enterprise
  Agent Hackathon. Covers getting an API key/credits, the OpenAI-compatible
  endpoint, recommended models (Nemotron-3 Super 120B), function/tool calling to
  drive CRAFT MCP tools, streaming, batch, embeddings, LiteLLM/LangChain/LangGraph
  wiring, and troubleshooting. Trigger whenever an agent needs to call an LLM,
  configure inference, pick a model, do function calling, or connect its
  reasoning model to the CRAFT data platform during the hackathon.
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

1. Claim credits at **https://dev.nebius.com/builders** (apply early — approval can lag).
2. Copy your **API key** and the **base URL** from the Token Factory dashboard.
3. Export it:
   ```bash
   export NEBIUS_API_KEY="your-key-here"
   # OpenAI-compatible base URL (confirm the exact value in your dashboard):
   export NEBIUS_BASE_URL="https://api.studio.nebius.com/v1/"
   ```

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

- **Default for agents / tool use:** `nvidia/nemotron-3-super-120b-a12b`
  (Nemotron-3 Super 120B, ~12B active, 1M context, **native function calling**).
- Token Factory hosts many open models (Llama, Qwen, DeepSeek, Kimi, etc.). Pick the smallest
  model that reliably tool-calls for your loop; scale up only if reasoning quality needs it.
- Full guidance + model IDs: `reference/models.md`.

## 4. Function calling → CRAFT

The whole game is: model proposes a tool call → you run the CRAFT MCP tool → return the result.
Minimal loop and a full LangGraph example: `reference/function-calling.md` and
`examples/function_calling_craft.py`.

## 5. Framework wiring (pick your stack)

- **OpenAI SDK** — set `base_url` + `api_key` (above).
- **LiteLLM** — `model="nebius/nvidia/nemotron-3-super-120b-a12b"`, `NEBIUS_API_KEY` set.
- **LangChain / LangGraph** — `ChatOpenAI(base_url=..., api_key=..., model=...)`.
- **Claude Code / Codex CLI** — route through a proxy (see `reference/api.md` → "CLI routing").

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
| `reference/troubleshooting.md` | Common errors and fixes |
| `examples/` | Runnable Python: quickstart, LiteLLM, function calling, LangGraph+CRAFT |

## Related resources

- **Token Factory Cookbook** — 50 recipes / 27 notebooks: https://github.com/nebius/token-factory-cookbook
- **Ecosystem cookbook mirror** — https://github.com/opencolin/nebius-ecosystem-cookbook
- **awesome-nebius** — curated Nebius resources: https://github.com/opencolin/awesome-nebius
- **Claude Code / Codex → Nebius proxy** — https://github.com/opencolin/claude-codex-nebius-proxy
- **openclaw-nebius-plugin** — https://github.com/opencolin/openclaw-nebius-plugin

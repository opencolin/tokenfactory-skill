# Token Factory API Reference

Token Factory is **OpenAI-compatible**. If a tool speaks OpenAI, point it at Nebius.

## Endpoint & auth

| Setting | Value |
|---|---|
| Base URL | `https://api.tokenfactory.nebius.com/v1` *(confirm the exact value in your Token Factory dashboard)* |
| Auth | `Authorization: Bearer $NEBIUS_API_KEY` |
| API key | From the dashboard / https://dev.nebius.com/builders |
| Wire format | OpenAI Chat Completions (`/chat/completions`), Embeddings (`/embeddings`), Batch, Models (`/models`) |

```bash
export NEBIUS_API_KEY="your-key"
export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
```

## curl

```bash
curl "$NEBIUS_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $NEBIUS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nvidia/nemotron-3-super-120b-a12b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

List available models:

```bash
curl "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY"
```

## Python (OpenAI SDK)

```python
from openai import OpenAI
import os

client = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])

r = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",
    messages=[{"role": "user", "content": "Explain a p95 latency spike in one line."}],
    temperature=0.2,
)
print(r.choices[0].message.content)
```

### Streaming

```python
stream = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",
    messages=[{"role": "user", "content": "Stream a haiku."}],
    stream=True,
)
for chunk in stream:
    delta = chunk.choices[0].delta.content or ""
    print(delta, end="", flush=True)
```

### Structured output (JSON)

```python
r = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b",
    messages=[{"role": "user", "content": "Return {\"ok\": true} as JSON."}],
    response_format={"type": "json_object"},
)
```

## JavaScript / TypeScript

```js
import OpenAI from "openai";
const client = new OpenAI({
  baseURL: process.env.NEBIUS_BASE_URL,   // https://api.tokenfactory.nebius.com/v1
  apiKey: process.env.NEBIUS_API_KEY,
});
const r = await client.chat.completions.create({
  model: "nvidia/nemotron-3-super-120b-a12b",
  messages: [{ role: "user", content: "Hello!" }],
});
console.log(r.choices[0].message.content);
```

## LiteLLM

```python
import litellm  # pip install litellm
# LiteLLM reads NEBIUS_API_KEY from the environment
r = litellm.completion(
    model="nebius/nvidia/nemotron-3-super-120b-a12b",
    messages=[{"role": "user", "content": "Hello from LiteLLM"}],
)
print(r.choices[0].message.content)
```

LiteLLM model string format: `nebius/<model-id>` (e.g. `nebius/nvidia/nemotron-3-super-120b-a12b`).

## LangChain / LangGraph

Use `ChatOpenAI` pointed at Nebius (works anywhere LangChain expects an OpenAI chat model):

```python
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    base_url=os.environ["NEBIUS_BASE_URL"],
    api_key=os.environ["NEBIUS_API_KEY"],
    model="nvidia/nemotron-3-super-120b-a12b",
    temperature=0.2,
)
```

Bind CRAFT MCP tools with `llm.bind_tools([...])` — see `function-calling.md`.

## CLI routing (Claude Code / Codex)

Token Factory is not Anthropic-shaped, so the Claude Code and Codex CLIs need a small proxy
that translates `/v1/messages` (Claude) and `/v1/responses` (Codex) to OpenAI calls:

- **claude-codex-nebius-proxy** (batteries-included, Nebius-tuned):
  https://github.com/opencolin/claude-codex-nebius-proxy
- Lighter alternatives: `claude-code-router`, or the LiteLLM proxy's Anthropic surface.

Not sure which CLI the user has? `claude --version` / `codex --version` in their terminal —
whichever answers is what they're running. The two are configured differently:

### Claude Code (Anthropic wire format)

1. Store the key in your shell (see SKILL.md §1): `export NEBIUS_API_KEY="..."` — persist it
   in `~/.zshrc` (macOS) or `~/.bashrc` (Linux).
2. Run the proxy locally (it reads `NEBIUS_API_KEY` from the environment — follow the proxy's
   README for the exact start command and port).
3. Point Claude Code at the proxy, e.g. `export ANTHROPIC_BASE_URL="http://127.0.0.1:8082"`
   (exact variable/port per the proxy's README).

### Codex CLI (Responses wire format)

Same proxy, then reference the key **indirectly** via `env_key` in `~/.codex/config.toml`:

```toml
model = "nebius/moonshotai/Kimi-K2.6"
model_provider = "nebius"
[model_providers.nebius]
name = "Nebius Proxy"
base_url = "http://127.0.0.1:8083/v1"
env_key = "OPENAI_API_KEY"
wire_api = "responses"
```

Set `OPENAI_API_KEY=$NEBIUS_API_KEY` in the shell so `env_key` resolves.

**Security on both paths:** the key only ever lives in environment variables. Never write the
raw key into `config.toml`, launch scripts, or anything that could be committed or shared.

## Notes

- Everything is OpenAI-shaped: `temperature`, `max_tokens`, `tools`, `tool_choice`,
  `response_format`, `stream` all behave as in the OpenAI SDK.
- Confirm the exact base URL and any model-name casing from your dashboard / the hackathon guide
  at https://www.emergence.ai/hackathon-checklist.

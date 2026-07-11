# CRAFT + Token Factory — End to End

The hackathon architecture:

```
                 tool calls                         MCP
  ┌─────────┐  ───────────────►  ┌───────────────┐ ─────► ┌──────────────────┐
  │  Your   │                    │  Your agent   │        │  CRAFT MCP server │──► Snowflake
  │  model  │  ◄───────────────  │  (glue code)  │ ◄───── │  (Text2SQL, etc.) │    (read-only)
  │ (Nebius)│   tool results     └───────────────┘  data  └──────────────────┘
  └─────────┘
```

- **Token Factory** runs the *reasoning* model (Nemotron) that decides what to do.
- **CRAFT (over MCP)** does the *data work*: schema discovery, NL→SQL, execution, charts.
- **Your glue code** relays tool calls from the model to CRAFT and results back.

## Two ways to connect the model to CRAFT

### A) Manual dispatch (most control)
Use the function-calling loop in `function-calling.md`. You keep an MCP client to CRAFT and, when
the model emits a tool call, you invoke the matching CRAFT MCP tool.

Minimal MCP client (Python `mcp` package):

```python
from mcp import ClientSession
from mcp.client.sse import sse_client   # or stdio_client, depending on CRAFT's transport
import os

# CRAFT MCP endpoint + auth come from the hackathon guide / your CRAFT account.
CRAFT_MCP_URL = os.environ["CRAFT_MCP_URL"]      # e.g. https://craft.emergence.ai/mcp
CRAFT_API_KEY = os.environ["CRAFT_API_KEY"]

async def craft_session():
    async with sse_client(CRAFT_MCP_URL, headers={"Authorization": f"Bearer {CRAFT_API_KEY}"}) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            tools = await session.list_tools()      # discover real tool names/params
            return session, tools
```

Then: `await session.call_tool(name, arguments)` inside your model loop.

### B) Framework MCP adapter (least glue)
Frameworks like LangGraph / LangChain can load MCP tools directly and bind them to a
`ChatOpenAI` pointed at Token Factory — the framework handles the dispatch loop for you.
See `examples/langgraph_craft_agent.py`.

## The core CRAFT tool loop

One analytical question typically = three MCP calls:

```
generate_sql  →  execute_query  →  get_result_page
```

Plus `get_schema` / `search_schema` for discovery and `generate_plotly_chart` for visuals.
**Let CRAFT own the SQL** — the model should call `generate_sql`, not write SQL itself. That is
exactly what judges reward ("CRAFT usage depth").

## Discover tools at runtime — don't hardcode

CRAFT's MCP server advertises its own tools. Always `list_tools()` first and build your
OpenAI `tools` array from that, so names/params match the live server.

## Environment summary

```bash
# Inference (Nebius Token Factory)
export NEBIUS_API_KEY="..."
export NEBIUS_BASE_URL="https://api.studio.nebius.com/v1/"
# Data (CRAFT over MCP) — values from the hackathon guide / your account
export CRAFT_MCP_URL="https://craft.emergence.ai/mcp"
export CRAFT_API_KEY="..."
```

Guide & checklist: https://www.emergence.ai/hackathon-checklist
Starter repo: https://github.com/EmergenceAI/nebius-emergence-hackathon

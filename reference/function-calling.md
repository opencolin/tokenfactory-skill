# Function / Tool Calling → CRAFT

Nemotron on Token Factory supports OpenAI-style tool calling. The agent loop is:

1. Send `messages` + `tools` to the model.
2. Model returns `tool_calls` (name + JSON args).
3. **You execute the tool** — for this hackathon, dispatch to a **CRAFT MCP tool**.
4. Append the tool result as a `role: "tool"` message.
5. Loop until the model answers with no more tool calls.

## Declaring CRAFT tools to the model

Expose CRAFT's MCP tools to the model as OpenAI function schemas. Example for the core loop:

```python
tools = [
    {"type": "function", "function": {
        "name": "get_schema",
        "description": "List tables/columns for a database in the CRAFT platform.",
        "parameters": {"type": "object", "properties": {
            "database": {"type": "string"}}, "required": ["database"]}}},
    {"type": "function", "function": {
        "name": "generate_sql",
        "description": "Translate a natural-language question into SQL for a database.",
        "parameters": {"type": "object", "properties": {
            "database": {"type": "string"},
            "question": {"type": "string"}}, "required": ["database", "question"]}}},
    {"type": "function", "function": {
        "name": "execute_query",
        "description": "Run SQL and return an artifact reference to the results.",
        "parameters": {"type": "object", "properties": {
            "sql": {"type": "string"}}, "required": ["sql"]}}},
    {"type": "function", "function": {
        "name": "generate_plotly_chart",
        "description": "Turn a result set into a Plotly figure.",
        "parameters": {"type": "object", "properties": {
            "artifact_id": {"type": "string"},
            "spec": {"type": "string"}}, "required": ["artifact_id"]}}},
]
```

> The exact CRAFT tool names/params come from the MCP server itself — list them at runtime
> (see `craft-integration.md`). Treat the schemas above as the shape, not the source of truth.

## The loop (OpenAI SDK)

```python
from openai import OpenAI
import json, os

client = OpenAI(base_url=os.environ["NEBIUS_BASE_URL"], api_key=os.environ["NEBIUS_API_KEY"])
MODEL = "nvidia/nemotron-3-super-120b-a12b"

def call_craft_tool(name, args):
    # Dispatch to the CRAFT MCP server (see craft-integration.md for the MCP client).
    return craft_mcp.call_tool(name, args)   # returns a JSON-serializable result

messages = [
    {"role": "system", "content": "You investigate enterprise data using the provided tools. "
                                   "Prefer generate_sql over writing SQL yourself."},
    {"role": "user", "content": "What are the top 6 product categories by spend for customer 42?"},
]

while True:
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, tools=tools, tool_choice="auto")
    msg = resp.choices[0].message
    messages.append(msg)

    if not msg.tool_calls:
        print(msg.content)   # final answer
        break

    for tc in msg.tool_calls:
        args = json.loads(tc.function.arguments or "{}")
        result = call_craft_tool(tc.function.name, args)
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result),
        })
```

## Tips

- **Guide the model** in the system prompt: use `generate_sql` (don't hand-write SQL), page large
  results, and stop once the question is answered.
- **Keep tool results compact** — pass row summaries or artifact references, not thousands of raw
  rows, to stay within context and keep the model focused.
- **Handle malformed args**: models occasionally emit slightly invalid JSON — wrap `json.loads`
  in a try/except and, on failure, return an error message as the tool result so the model retries.
- **`tool_choice`**: use `"auto"` normally; force a specific tool with
  `{"type": "function", "function": {"name": "get_schema"}}` when you want to seed discovery.

"""Function-calling loop: Nemotron (Token Factory) drives CRAFT MCP tools.

This is the core hackathon pattern. Replace `call_craft_tool` with real CRAFT MCP
dispatch (see reference/craft-integration.md for an MCP client). The tool SCHEMAS here
are illustrative — discover the real ones from CRAFT with list_tools() at runtime.

Setup:
    pip install openai
    export NEBIUS_API_KEY="your-key"
    export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
"""
import os, json
from openai import OpenAI

client = OpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
)
MODEL = "nvidia/nemotron-3-super-120b-a12b"

TOOLS = [
    {"type": "function", "function": {
        "name": "generate_sql",
        "description": "Translate a natural-language question into SQL for a database.",
        "parameters": {"type": "object",
            "properties": {"database": {"type": "string"}, "question": {"type": "string"}},
            "required": ["database", "question"]}}},
    {"type": "function", "function": {
        "name": "execute_query",
        "description": "Run SQL and return the result rows.",
        "parameters": {"type": "object",
            "properties": {"sql": {"type": "string"}}, "required": ["sql"]}}},
]


def call_craft_tool(name, args):
    """STUB — wire this to the CRAFT MCP server (session.call_tool)."""
    if name == "generate_sql":
        return {"sql": f"-- SQL for: {args['question']} (from CRAFT)"}
    if name == "execute_query":
        return {"rows": [{"category": "Jumpsuits & Rompers", "spend": 412.0}]}
    return {"error": f"unknown tool {name}"}


def run(question, database="THELOOK_ECOMMERCE"):
    messages = [
        {"role": "system", "content": "You investigate enterprise data. Always use generate_sql; "
                                      "never hand-write SQL. Stop when the question is answered."},
        {"role": "user", "content": f"[database={database}] {question}"},
    ]
    for _ in range(12):  # safety bound on tool-calling turns
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS, tool_choice="auto")
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
                result = call_craft_tool(tc.function.name, args)
            except Exception as e:  # return errors to the model so it can recover
                result = {"error": str(e)}
            messages.append({"role": "tool", "tool_call_id": tc.id,
                             "content": json.dumps(result)})
    return "(stopped: too many tool-calling turns)"


if __name__ == "__main__":
    print(run("What are the top categories by spend for customer 42?"))

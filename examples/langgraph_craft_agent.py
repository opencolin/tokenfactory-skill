"""LangGraph agent: Nemotron on Token Factory + CRAFT MCP tools (adapter approach).

Frameworks can load MCP tools and run the tool-dispatch loop for you. Here LangGraph's
prebuilt ReAct agent uses a ChatOpenAI pointed at Token Factory, with CRAFT's MCP tools
loaded via langchain-mcp-adapters.

Setup:
    pip install langgraph langchain-openai langchain-mcp-adapters
    export NEBIUS_API_KEY="your-key"
    export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"
    export CRAFT_MCP_URL="https://craft.emergence.ai/mcp"   # from the hackathon guide
    export CRAFT_API_KEY="your-craft-key"
"""
import os, asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatOpenAI(
    base_url=os.environ.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1"),
    api_key=os.environ["NEBIUS_API_KEY"],
    model="nvidia/nemotron-3-super-120b-a12b",
    temperature=0.2,
)


async def main():
    client = MultiServerMCPClient({
        "craft": {
            "url": os.environ["CRAFT_MCP_URL"],
            "transport": "sse",
            "headers": {"Authorization": f"Bearer {os.environ['CRAFT_API_KEY']}"},
        }
    })
    tools = await client.get_tools()            # real CRAFT tools, discovered live
    agent = create_react_agent(llm, tools)

    result = await agent.ainvoke({"messages": [
        {"role": "system", "content": "Investigate enterprise data with CRAFT. Use generate_sql; "
                                      "don't hand-write SQL."},
        {"role": "user", "content": "Where does the onboarding funnel lose the most mobile users?"},
    ]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())

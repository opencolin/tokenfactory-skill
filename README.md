# tokenfactory-skill

Everything an agent (or a hacker) needs to use **Nebius Token Factory** for LLM inference in the
**Emergence × Nebius Enterprise Agent Hackathon**.

Token Factory serves open models behind an **OpenAI-compatible API**. Point your agent at it by
setting a **base URL**, an **API key**, and a **model name** — then let your model reason and
**call CRAFT's MCP tools** to do the data work.

> **TL;DR**
> ```bash
> export NEBIUS_API_KEY="your-key-here"          # from https://dev.nebius.com/builders
> export NEBIUS_BASE_URL="https://api.tokenfactory.nebius.com/v1"   # confirm in dashboard
>
> # Persist across sessions:
> echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.zshrc    # macOS
> echo 'export NEBIUS_API_KEY="your-key-here"' >> ~/.bashrc   # Linux
>
> # model: nvidia/nemotron-3-super-120b-a12b
> ```
>
> New to Token Factory? `SKILL.md` §1 walks you from zero (get a key, store it securely,
> verify with one curl). Using Claude Code or Codex? See `reference/api.md` → "CLI routing".

## What's here

```
tokenfactory-skill/
├── SKILL.md                        # start here — the skill entry point
├── .env.example                    # env vars template (Nebius + CRAFT)
├── reference/
│   ├── api.md                      # endpoints, auth, curl/Python/JS, LiteLLM, LangChain, CLI routing
│   ├── models.md                   # recommended models + IDs (Nemotron-3 Super 120B)
│   ├── function-calling.md         # tool-calling loop → CRAFT MCP
│   ├── batch-and-embeddings.md     # batch evals + embeddings for RAG
│   ├── craft-integration.md        # CRAFT-over-MCP + Token Factory, end to end
│   ├── proxy-setup.md              # install claude-codex-nebius-proxy (Claude Code / Codex)
│   └── troubleshooting.md          # common errors & fixes
└── examples/
    ├── quickstart_openai.py        # first call (OpenAI SDK)
    ├── litellm_nemotron.py         # via LiteLLM
    ├── function_calling_craft.py   # Nemotron drives CRAFT tools (manual loop)
    └── langgraph_craft_agent.py    # LangGraph + MCP adapter (framework loop)
```

## Using it as an agent skill

Drop this folder into your agent's skills directory (or point your loader at `SKILL.md`).
The frontmatter `description` tells the agent when to use it; the body links to the reference
files on demand.

## Hackathon links

- Hub & guide: https://www.emergence.ai/hackathon-checklist
- Starter repo: https://github.com/EmergenceAI/nebius-emergence-hackathon
- Get credits: https://dev.nebius.com/builders
- Community Slack `#help` for live support

## Related (Nebius ecosystem)

- **Token Factory Cookbook** (50 recipes): https://github.com/nebius/token-factory-cookbook
- **nebius-devsite** — open-source projects from past hackathons: https://github.com/opencolin/nebius-devsite
- **awesome-nebius**: https://github.com/opencolin/awesome-nebius
- **nebius-ecosystem-cookbook**: https://github.com/opencolin/nebius-ecosystem-cookbook
- **claude-codex-nebius-proxy** (route Claude Code/Codex → Nebius): https://github.com/opencolin/claude-codex-nebius-proxy
- **openclaw-nebius-plugin**: https://github.com/opencolin/openclaw-nebius-plugin

## Notes on accuracy

Model IDs, the exact base URL, and Batch availability can change — always trust the live
`GET /models` endpoint and the hackathon guide over any hardcoded value in these docs.
Values marked *"confirm in dashboard"* should be verified from your Token Factory account.

## License

MIT (docs and example code). Nebius, Token Factory, and product names belong to Nebius B.V.

# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` | Missing/expired key, or key not yet approved | Re-copy the key from the dashboard; confirm credits approved at https://dev.nebius.com/builders; ensure `Authorization: Bearer $NEBIUS_API_KEY`. |
| `404` / "model not found" | Wrong model ID or casing | Call `GET /models` and copy the exact ID (e.g. `nvidia/nemotron-3-super-120b-a12b`). |
| Connection errors / wrong host | Wrong base URL | Use the OpenAI-compatible base URL from your dashboard (commonly `https://api.studio.nebius.com/v1/`); include the trailing `/v1/`. |
| Helper expects `OPENAI_API_KEY` | Tool only reads OpenAI vars | Set `OPENAI_API_KEY=$NEBIUS_API_KEY` and `OPENAI_BASE_URL=$NEBIUS_BASE_URL`. |
| `429` / rate limit | Too many concurrent requests | Add retry with backoff; cap concurrency (semaphore); use the Batch API for bulk evals. |
| Context length exceeded | Oversized tool results in history | Summarize/paginate results; pass artifact references not raw rows; trim old tool messages. |
| Model returns invalid tool-call JSON | Occasional malformed args | `try/except` around `json.loads`; on failure return an error tool-result so the model retries. |
| Model writes SQL instead of calling `generate_sql` | Weak system prompt | Instruct explicitly: "Always use `generate_sql`; never hand-write SQL." Consider `tool_choice` to force it. |
| Claude Code / Codex won't use Nebius | CLIs are Anthropic-shaped | Route through a proxy (`opencolin/claude-codex-nebius-proxy`, `claude-code-router`, or LiteLLM proxy). |
| Streaming shows nothing | Consuming deltas wrong | Read `chunk.choices[0].delta.content` (may be `None` on some chunks). |

## Fast sanity check

```bash
curl -s "$NEBIUS_BASE_URL/models" -H "Authorization: Bearer $NEBIUS_API_KEY" | head
```

If that returns a model list, your key + base URL are correct and the problem is in the request
(model name, message shape, or tool schema).

## Where to get help during the event

- Live support: **EmergenceAI Community Slack** `#help`
- Guide: https://www.emergence.ai/hackathon-checklist
- Nebius recipes: https://github.com/nebius/token-factory-cookbook

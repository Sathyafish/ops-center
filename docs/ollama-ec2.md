# Ollama on EC2 (local LLM for Ops Center GraphRAG)

Use **Ollama on the EC2 host** for chat (`llama3.2:3b`) and **embeddings** (`nomic-embed-text`) while Neo4j/Chroma/API stay in Docker.

## 1. Install and run Ollama on Amazon Linux 2023

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
```

Pull models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Quick test:

```bash
ollama run llama3.2:3b "Say OK in one word."
```

## 2. Allow Docker API container to reach Ollama

Ollama listens on `127.0.0.1:11434` on the host. `docker-compose.yml` maps **`host.docker.internal`** → host gateway for the `api` service.

If connection fails, set Ollama to listen on all interfaces (optional):

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Then in `backend/.env` you can use the host private IP instead:

```env
OLLAMA_BASE_URL=http://10.x.x.x:11434
```

Lock security group so **11434** is not open to the public internet.

## 3. Configure `backend/.env`

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2:3b

EMBEDDING_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# Smaller context helps 3B models
LLM_CONTEXT_MAX_CHARS=6000

# OpenAI not required when both providers are ollama (leave empty or omit)
OPENAI_API_KEY=
```

**Important:** If you only set `LLM_PROVIDER=ollama` but leave `EMBEDDING_PROVIDER=openai`, `seed_all` will fail without an OpenAI key. Set **both** to `ollama`, or leave `OPENAI_API_KEY` empty (the app auto-aligns embeddings to Ollama when LLM is Ollama and no OpenAI key).

## 4. Rebuild API and re-index vectors

Embeddings change when switching to Ollama — rebuild Chroma:

```bash
cd ~/ops-center
export NEO4J_PASSWORD='your-password'
docker compose build --no-cache api
docker compose up -d
docker compose exec api python -m app.scripts.seed_all
```

## 5. Verify

```bash
curl -s http://localhost:8000/health
# expect llm_provider: ollama, embedding_provider: ollama

docker compose exec api curl -s http://host.docker.internal:11434/api/tags
```

Log in to the UI and run a graph question, e.g. “Who is the SME for PaymentGateway?”

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Connection refused to Ollama | Check `systemctl status ollama`; test from host `curl localhost:11434/api/tags` |
| API cannot reach host | Confirm `extra_hosts: host.docker.internal:host-gateway` on `api` service |
| Empty / bad vector search | Re-run `seed_all` after pulling `nomic-embed-text` |
| Slow answers | Normal on `t3.large` + 3B; use `LLM_CONTEXT_MAX_CHARS=4000` or a larger instance |

## Hybrid (optional)

Chat local, embeddings OpenAI:

```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

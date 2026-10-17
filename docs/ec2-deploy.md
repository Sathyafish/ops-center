# Deploy Ops Center GraphRAG on AWS EC2

## Instance sizing

- **Recommended:** `t3.large` (2 vCPU, 8 GB RAM) — Neo4j + Chroma + API + nginx frontend
- **OS:** Ubuntu 22.04 LTS
- **Storage:** 30 GB gp3 minimum

## Security groups

| Port | Source | Purpose |
|------|--------|---------|
| 22 | Your IP | SSH |
| 80 | Your IP or VPN | Frontend (or 443 with TLS) |
| 8000 | Optional — prefer reverse proxy only | API |
| 7474 | **Do not expose publicly** | Neo4j Browser — use SSH tunnel |

## Setup steps

```bash
# On EC2
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER
# Log out and back in

git clone <your-repo-url> ops-center && cd ops-center
cp backend/.env.example backend/.env
nano backend/.env   # OPENAI_API_KEY, strong JWT_SECRET, NEO4J_PASSWORD

export NEO4J_PASSWORD='your-strong-password'
docker compose up -d --build
docker compose exec api python -m app.scripts.seed_all
```

## TLS (recommended)

Put **Caddy** or **nginx** on the host in front of `frontend:80`, terminate TLS with ACM or Let's Encrypt.

Update `CORS_ORIGINS` in `backend/.env` to your public URL.

## Neo4j access

```bash
ssh -L 7474:localhost:7474 ubuntu@<ec2-ip>
# Open http://localhost:7474
```

## Health checks

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"ops.alice","password":"OpsCenter2026!"}'
```

## Production hardening

- Rotate all 5 user passwords; consider moving users to a database or IdP
- Restrict SG to corporate VPN
- Use AWS Secrets Manager for `OPENAI_API_KEY` and `JWT_SECRET`
- Enable Neo4j backups on the `neo4j_data` volume snapshot schedule

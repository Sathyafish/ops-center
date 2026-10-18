# Deploy Ops Center GraphRAG on AWS EC2 (Amazon Linux 2023)

## Instance sizing

- **Recommended:** `t3.large` (2 vCPU, 8 GB RAM) — Neo4j + Chroma + API + nginx frontend
- **OS:** **Amazon Linux 2023** (select the official AMI in EC2 launch wizard)
- **Login user:** `ec2-user`
- **Storage:** 30 GB gp3 minimum

## Security groups

| Port | Source | Purpose |
|------|--------|---------|
| 22 | Your IP | SSH |
| 80 | Your IP or VPN | Frontend (or 443 with TLS) |
| 8000 | Optional — prefer reverse proxy only | API |
| 7474 | **Do not expose publicly** | Neo4j Browser — use SSH tunnel |
| 7687 | **Do not expose publicly** | Bolt — API container only (Docker network) |

## Install Docker and Compose (Amazon Linux 2023)

```bash
sudo dnf update -y
sudo dnf install -y docker git

sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -SL "https://github.com/docker/compose/releases/download/v2.29.2/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
```

Log out and SSH back in as `ec2-user`, then:

```bash
docker compose version
git clone <your-repo-url> ops-center && cd ops-center
cp backend/.env.example backend/.env
nano backend/.env   # OPENAI_API_KEY, JWT_SECRET, NEO4J_PASSWORD

export NEO4J_PASSWORD='your-strong-password'
cd ~/ops-center   # must be repo root, not backend/
docker compose up -d --build
docker compose exec api python -m app.scripts.seed_all
```

Neo4j setup details (password sync, verify, backup, SSH tunnel): see **EC2 deployment** in [README.md](../README.md).

**Local LLM (Ollama):** [ollama-ec2.md](ollama-ec2.md) — `llama3.2:3b` + `nomic-embed-text`, `LLM_PROVIDER=ollama` in `backend/.env`.

## TLS (recommended)

Put **Caddy** or **nginx** on the host in front of `frontend:80`, terminate TLS with ACM or Let's Encrypt.

Update `CORS_ORIGINS` in `backend/.env` to your public URL.

## Neo4j Browser access (SSH tunnel)

From your laptop:

```bash
ssh -i ~/.ssh/your-key.pem -L 7474:127.0.0.1:7474 ec2-user@<ec2-public-ip>
```

Open http://localhost:7474 — Bolt URL `bolt://localhost:7687`, user `neo4j`, password from `NEO4J_PASSWORD`.

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
- Enable Neo4j backups on the `neo4j_data` volume / EBS snapshot schedule

## SELinux (Amazon Linux 2023)

Docker bind mounts and published ports work with default policies. If you run a host-level reverse proxy with non-standard paths, use `sudo setsebool -P httpd_can_network_connect 1` only when required for proxy → container traffic.

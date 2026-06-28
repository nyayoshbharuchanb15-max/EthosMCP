# AI Governance MCP Server: Deployment Guide

This guide provides instructions for deploying the AI Governance MCP Server in an on-premise, zero-data-egress environment using Docker.

## 1. Prerequisites
- Docker Engine 24.0+
- Docker Compose 2.20+
- Minimum 8GB RAM and 4 CPU cores
- 20GB free disk space for database volumes

## 2. Configuration
Copy `.env.example` to `.env` and configure the following:
```bash
cp .env.example .env
```
Key parameters:
- `CRYPTO_KEY`: A secure 32-byte key for HMAC signatures.
- `ISSUER_DID`: The DID of the authority issuing audit certificates.
- `ENABLE_LIVE_REGULATORY_FEEDS`: Set to `false` for air-gapped or high-security environments.

## 3. On-Premise Deployment
The entire stack can be launched using a single command:
```bash
docker-compose up -d --build
```

### Services Started:
- `mcp-server`: TypeScript interface layer (Port 3100)
- `api`: FastAPI backend orchestrator (Port 8000)
- `postgres`: Immutable evidence store (Internal only)
- `neo4j`: Provenance graph database (Internal only)
- `nats`: High-speed messaging for webhooks (Internal only)

## 4. Verification
Check the health of all services:
```bash
curl http://localhost:8000/health
```
Verify MCP server registration:
```bash
# Using a tool like mcp-cli or connecting via Claude Desktop
mcp-cli list-tools
```

## 5. Security Best Practices
- **Network Isolation**: The default `docker-compose.yml` uses an internal bridge network `governance-net` with `internal: true`. This prevents all outbound traffic.
- **Volume Encryption**: Ensure the host filesystem where `postgres_data` and `neo4j_data` are stored is encrypted at rest.
- **Secrets Management**: For production, avoid plain-text `.env` files and use Docker Secrets or a dedicated vault.
- **Regular Backups**: Implement automated backups for the Postgres and Neo4j volumes to ensure business continuity.

## 6. Troubleshooting
- **Database Connection**: If the API fails to start, check if Postgres is healthy using `docker-compose ps`.
- **Memory Limits**: Neo4j can be memory-intensive. If it crashes, increase the allocated RAM in the host or container configuration.
- **Log Inspection**:
```bash
docker-compose logs -f api
docker-compose logs -f mcp-server
```

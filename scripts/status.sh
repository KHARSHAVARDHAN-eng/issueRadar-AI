#!/bin/bash
set -e

echo "📊 IssueRadar AI Local Stack Status:"
docker compose ps

echo -e "\n🏥 Backend Health Inspection (/health):"
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Backend unreachable"

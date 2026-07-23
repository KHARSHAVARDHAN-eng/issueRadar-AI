#!/bin/bash
set -e

echo "🚀 Starting IssueRadar AI Local Production Stack..."
docker compose up --build -d

echo "⏳ Waiting for backend container to report healthy status..."
sleep 5

docker compose ps

echo "Checking backend /health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Backend starting up..."

echo "✅ Local deployment successfully initiated at http://localhost:8000"

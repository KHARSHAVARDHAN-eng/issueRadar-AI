# Changelog - IssueRadar AI

All notable changes to **IssueRadar AI** are documented in this file.
The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-24

### 🌟 Milestone Highlights

- **Production Monorepo & Architecture**: Production-ready monorepo with React 18 + Vite + TypeScript web application, FastAPI Python backend, PostgreSQL 16, and Redis 7.
- **GitHub Authentication**: Production-ready GitHub OAuth 2.0 flow, Fernet-encrypted GitHub token storage, and HttpOnly session cookies.
- **Repository Management**: CRUD repository endpoints, GitHub REST API integration, star/fork metadata tracking, and duplicate prevention.
- **GitHub Sync Engine**: Asynchronous synchronization pipeline upserting issues, labels, comments, and pull requests with Redis job tracking.
- **Rule-Based Scoring Engine**: Deterministic issue quality scoring algorithm analyzing bug labels, reproduction steps, comment density, and unassigned status.
- **AI Issue Analyzer**: Structured LLM provider pipeline analyzing issue complexity, difficulty classification, estimated effort, and merge probability.
- **Smart Discovery & Advanced Search**: Full-text issue search, multi-factor filtering, and dynamic sorting engine (`score_desc`, `merge_desc`, `created_desc`).
- **AI Issue Coach**: Actionable developer onboarding instructions including problem explanations, step-by-step implementation plans, required knowledge, and testing strategies.
- **Automation & Notification Engine**: Saved search filters, issue bookmarking, and automated background sync notifications.
- **Production AI Provider Architecture**: Pluggable provider system with `MockLLMProvider`, `GeminiProvider`, and `OpenAIProvider` with transient failure retries and structured JSON output.
- **Celery Background Workers**: Production Celery background workers (`task_sync_repository`, `task_analyze_repository`, `task_scan_notifications`) with non-blocking pipeline chaining.
- **Enterprise Engineering & Reliability**: Redis caching, sliding-window rate limiting, structured JSON logging, Kubernetes probes (`/ready`, `/live`), Prometheus metrics (`/metrics`), and JWT refresh token rotation.
- **Production DevOps & Deployment**: Multi-stage Dockerfiles, `docker-compose.prod.yml`, Nginx edge reverse proxy, GitHub Actions CI/CD pipeline, and `Makefile` automation.

---
title: Production Deployment
summary: Hardening, monitoring, and blue/green deployment for the Factory.
weight: 50
---

## Readiness

- 90%+ API coverage, tests, error handling, type hints
- Security: tokens, rate limit, retries, timeouts

## Deploy

- Dockerfile.production and docker-compose.production.yml
- Health checks, auto-restart, 2+ replicas
- Prometheus + Grafana dashboards

## Zero Downtime

- Scale up new version; health check; scale down old

## KPIs

- Uptime 99.9%, p95 < 500ms, error rate < 0.1%

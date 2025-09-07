---
title: Microservices Architecture
summary: Service decomposition, data strategy, and communication patterns.
weight: 20
---

## Executive Summary

A DDD-aligned microservices architecture with clear service boundaries, independent scaling, and a multi-database strategy.

## Services

- Governance Core: governance-engine, issue-management, project-orchestration, analytics-reporting, event-processing
- Integrations: github-api, webhook-handler, agent-gateway, notification
- Data: configuration, audit & compliance, cache, state

## Datastores

- MongoDB: configuration, specs, state
- Supabase: issues, analytics, audit
- Redis: caching, streams, pub/sub

## Communications

- Sync: REST across services with retries and timeouts
- Async: Redis Streams for events like issue.created, project.updated

## KPIs

- p95 < 500ms, 99.9% uptime, >90% cache hit for hot paths

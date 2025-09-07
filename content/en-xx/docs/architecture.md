---
title: Platform Architecture
summary: End-to-end architecture of the GitHub Governance Factory with core services, data stores, and integration patterns.
weight: 10
---

## Overview

The GitHub Governance Factory is an enterprise-grade, AI-assisted governance automation platform. It transforms project specifications into governed Epic → Feature → Task hierarchies and manages the lifecycle across GitHub.

## Core Services

- Governance Engine (Port 8000): policy engine, project breakdown, health
- Issue Generator (Port 8001): issue creation, labels/milestones, repo setup
- Shared GitHub API Client: async wrapper with retries and rate-limit handling
- Databases: MongoDB (governance), Supabase (analytics), Redis (cache/events)

## Integration Pattern

- AI Provider Factory via HTTP: centralized, provider-agnostic AI calls
- Event-driven streams for webhooks and analytics via Redis
- Async-first service internals with health checks and structured logs

## Why it matters

- Clean separation of concerns and safer credentials handling
- Scales by service; supports enterprise observability and compliance

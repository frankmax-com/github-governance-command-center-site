---
title: GitHub API Wrapper
summary: Implemented capabilities, examples, and priority roadmap for missing functions.
weight: 30
---

## Status

Core repository, issues, labels, milestones, PRs, branches, webhooks, orgs, users, search, projects, and batch setup are implemented.

## Usage

- Setup governance: create labels, milestones, and defaults
- Create issues and comments; update and list by filters
- Manage PRs, branches, and webhooks

## Priorities (Phase 1)

- Repository: update_repository, fork_repository, get_repository_topics
- Issues: delete_issue_comment, list_issue_events, lock_issue
- Labels: update_label, add_labels_to_issue
- Files: get_file_contents, create_or_update_file
- PRs: update_pull_request, merge_pull_request

## Pattern

- Always obtain client via get_github_client(token)
- Async/await for all calls
- Retry and rate-limit handling baked in

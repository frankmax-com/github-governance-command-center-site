# GitHub Governance Factory — Website

Marketing website for the GitHub Governance Factory. Built with Hugo, multilingual (English `en-xx`, Chinese `zh-sg`), and deployed to GitHub Pages via Actions.

Site URL: https://frankmax-com.github.io/github-governance-command-center-site

## Branching and workflow (GitFlow)
- main/master: production (GitHub Pages). Deploys from these branches only.
- develop: integration. All features merge here first.
- feature/*: short-lived branches for changes. Open PRs into `develop`.

PRs run a build validation workflow (no deploy). Merges to main/master trigger the Pages deployment.

## CI/CD
- Deploy: `.github/workflows/hugo.yml` (push to main/master)
- PR Build: `.github/workflows/hugo-pr.yml` (pull_request to develop/main/master)
- Pages baseURL is auto-wired by the deploy workflow.

## Local development
```powershell
# Windows (PowerShell)
# Install Hugo Extended (one-time)
# choco install hugo-extended

# Start dev server with drafts
hugo server -D

# Build production assets
hugo --gc --minify
```

## Content & structure
- Layouts: `layouts/` (site shell in `_default/baseof.html`, homepage in `index.html`)
- Styles: `static/css/crisis.css`
- Content: `content/en-xx`, `content/zh-sg`
- Data: `data/*.yaml`
- Theme: submodule at `themes/frankmax`

Key pages
- Risk Register heatmap: `/risk-register`
- Master Threat Catalogue: `/master-threat-catalogue`
- CISO/Board Brief: `/ciso-board-brief`

## Opening a PR
1) Push your feature branch
2) Open PR into `develop`: compare `develop...your-feature-branch`
3) Ensure PR build (Hugo) passes
4) Merge to `develop`
5) Submit a follow-up PR from `develop` to `main` (or `master`) to deploy

## Notes
- The `public/` folder is a build output. It’s not needed for Pages deployments and can be excluded from commits.
- This repository contains only the website. Application/microservices docs live elsewhere.

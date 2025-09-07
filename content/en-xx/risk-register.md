---
Title: "Enterprise Risk Register Heatmap"
url: "/risk-register/"
layout: "single"
---

<section class="container">
  <header class="mb-8">
    <div class="hero-eyebrow">Board-ready</div>
    <h1>Enterprise GitHub Risk Register Heatmap</h1>
    <p class="lead">The 5 risk domains and their highest-impact threats enterprises face in GitHub today, with mapped defenses from the GitHub Governance Factory.</p>
  </header>

  <div class="chips mb-6">
    <span class="chip chip-high"><span class="dot"></span>Cybersecurity</span>
    <span class="chip chip-high"><span class="dot"></span>Compliance & Legal</span>
    <span class="chip chip-med"><span class="dot"></span>Operational Resilience</span>
    <span class="chip chip-med"><span class="dot"></span>Financial Governance</span>
    <span class="chip chip-med"><span class="dot"></span>Human & Organizational</span>
  </div>

  <div class="heatmap">
    <article class="hm-card">
      <h3 class="hm-title">Insider threat (code/IP exfiltration)</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-high" title="Impact severity">Severe</span>
      </div>
      <p class="hm-desc">GitHub logs actions but lacks behavioral anomaly detection and split-key repo exports.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Our defense</a>
        <a class="btn btn-secondary" href="{{ "/solutions/" | relURL }}">All defenses</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Credential/secret leakage</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-high">Severe</span>
      </div>
      <p class="hm-desc">Regex secret scanning is reactive; custom formats and configs slip through.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/zero-commit-data-firewall/" | relURL }}">Zero‑commit firewall</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Dependency poisoning (supply chain)</h3>
      <div class="hm-meta">
        <span>Likelihood: Medium</span>
        <span class="sev sev-high">Severe</span>
      </div>
      <p class="hm-desc">Limited Dependabot scope, no enforced provenance or enterprise trust gate.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/cryptographic-dependency-provenance/" | relURL }}">Provenance gate</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">GitHub Actions abuse</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-med">High</span>
      </div>
      <p class="hm-desc">Marketplace actions and misconfigurations create silent supply chain paths.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Policy guardrails</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">GDPR/HIPAA/PCI violations</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-high">Severe</span>
      </div>
      <p class="hm-desc">No right-to-delete in history; no data classification or regulator‑grade logs.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/sovereign-repo-enclaves/" | relURL }}">Sovereign enclaves</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Litigation & e‑discovery gaps</h3>
      <div class="hm-meta">
        <span>Likelihood: Medium</span>
        <span class="sev sev-med">High</span>
      </div>
      <p class="hm-desc">Logs are not immutable evidence; force‑push/rebase weakens chain‑of‑custody.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Immutable audit</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Disaster recovery gaps</h3>
      <div class="hm-meta">
        <span>Likelihood: Medium</span>
        <span class="sev sev-med">Severe</span>
      </div>
      <p class="hm-desc">No repo criticality awareness or tiered recovery orchestration.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Tiered DR</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">License waste & CI/CD overruns</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-med">Medium</span>
      </div>
      <p class="hm-desc">No budget caps, attribution, or automated seat harvesting.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/" | relURL }}">Cost guardrails</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Rubber‑stamp approvals</h3>
      <div class="hm-meta">
        <span>Likelihood: High</span>
        <span class="sev sev-med">High</span>
      </div>
      <p class="hm-desc">GitHub checks that approvals exist, not their independence or depth.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Multi‑sig merges</a>
      </div>
    </article>

    <article class="hm-card">
      <h3 class="hm-title">Meta‑governance void</h3>
      <div class="hm-meta">
        <span>Likelihood: Low</span>
        <span class="sev sev-cat">Catastrophic</span>
      </div>
      <p class="hm-desc">Admins can silently rewrite org policy; no second‑order control plane.</p>
      <div class="hm-actions">
        <a class="btn btn-primary" href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Immutable policy</a>
      </div>
    </article>
  </div>

  <div class="callout mt-10">
    <strong>Want the full 100‑risk register?</strong> Get the complete, board‑ready CSV and mapping to mitigations.
    <div class="hero-actions">
      <a class="btn btn-primary" href="{{ "/sitemap/" | relURL }}">Request download</a>
      <a class="btn btn-secondary" href="{{ "/solutions/" | relURL }}">Explore mitigations</a>
    </div>
  </div>
</section>

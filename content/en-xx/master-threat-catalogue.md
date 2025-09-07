---
Title: "Master Threat Catalogue"
url: "/master-threat-catalogue/"
layout: "single"
---

<section class="container">
  <header class="mb-8">
    <div class="hero-eyebrow">What could go wrong</div>
    <h1>Master Threat Catalogue: 45+ GitHub Enterprise Blind Spots</h1>
    <p class="lead">Condensed from your internal docs: data protection, compliance, operational, security, continuity, human, legal, systemic. Each category links to mapped defenses.</p>
  </header>

  <div class="stats mb-8">
    <div class="stat"><div class="value">45+</div><div class="label">Core risk categories</div></div>
    <div class="stat"><div class="value">100</div><div class="label">Board‑level risks (expanded)</div></div>
    <div class="stat"><div class="value">128</div><div class="label">Industry use cases</div></div>
  </div>

  <table class="matrix">
    <thead>
      <tr>
        <th>Category</th>
        <th>Examples</th>
        <th>Severity</th>
        <th>Mitigation</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Data protection gaps</td>
        <td>Unprotected secrets, PII/PHI in repos, cross‑border leakage</td>
        <td><span class="sev sev-high">High</span></td>
        <td><a href="{{ "/solutions/zero-commit-data-firewall/" | relURL }}">Zero‑commit data firewall</a>, <a href="{{ "/solutions/sovereign-repo-enclaves/" | relURL }}">Sovereign enclaves</a></td>
      </tr>
      <tr>
        <td>Governance & compliance failures</td>
        <td>No immutable audit, policy drift, no sector mappings</td>
        <td><span class="sev sev-high">High</span></td>
        <td><a href="{{ "/solutions/insider-proof-governance-grid/" | relURL }}">Immutable policy & audit</a></td>
      </tr>
      <tr>
        <td>Operational & catastrophic</td>
        <td>Single maintainer, repo sprawl, DR blind spots</td>
        <td><span class="sev sev-high">High</span></td>
        <td>Quorum ownership, lifecycle orchestration, tiered DR</td>
      </tr>
      <tr>
        <td>Security shortcomings</td>
        <td>Reactive scans, access creep, supply chain poisoning</td>
        <td><span class="sev sev-high">High</span></td>
        <td>Preventive firewall, zero‑privilege, provenance grid</td>
      </tr>
      <tr>
        <td>Resilience & continuity</td>
        <td>No criticality tagging, weak monitoring integration</td>
        <td><span class="sev sev-high">High</span></td>
        <td>Criticality DNA, telemetry mesh, self‑healing baseline</td>
      </tr>
      <tr>
        <td>Human & cultural</td>
        <td>Rubber‑stamp approvals, burnout, insider collusion</td>
        <td><span class="sev sev-med">Medium</span></td>
        <td>Multi‑sig merges, AI caretakers, split‑key exports</td>
      </tr>
      <tr>
        <td>Legal & contractual</td>
        <td>OSS license contamination, e‑discovery gaps</td>
        <td><span class="sev sev-high">High</span></td>
        <td>License scanning, immutable evidence, policy signing</td>
      </tr>
      <tr>
        <td>Meta‑governance void</td>
        <td>Admins can rewrite org policy; no second‑order control plane</td>
        <td><span class="sev sev-cat">Catastrophic</span></td>
        <td>Immutable policy ledger, multi‑party admin actions</td>
      </tr>
      <tr>
        <td>Civilization‑scale externalities</td>
        <td>Systemic concentration risk, global vendor outage</td>
        <td><span class="sev sev-cat">Catastrophic</span></td>
        <td>Portable repo sovereignty, multi‑vault mirroring</td>
      </tr>
    </tbody>
  </table>

  <div class="callout mt-10">
    <strong>Need the board deck?</strong> We can export this catalogue with Likelihood × Impact scoring and sector‑specific mappings.
    <div class="hero-actions">
      <a class="btn btn-primary" href="{{ "/risk-register/" | relURL }}">View heatmap</a>
      <a class="btn btn-secondary" href="{{ "/solutions/" | relURL }}">Map to defenses</a>
    </div>
  </div>
</section>

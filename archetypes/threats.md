---
# Title should include severity label for consistency
# Example: "🔴 Meta-Governance Void - CATASTROPHIC"
title: "${title}"
description: ""
threat_id: "TXXX"
# severity examples: CATASTROPHIC | COMPANY KILLER | HIGH | MEDIUM | LOW
severity: "CATASTROPHIC"
category: ""
audience: "Security & Exec"
date: {{ .Date }}
# Optional: explicit publish date override
# publishDate: {{ .Date }}
---

# ${title}

## What goes wrong
- Briefly explain the core failure mode and why it matters.

## Signals you’ll see
- 3–5 observable signals that indicate this threat is present.

## Business impact
- Quantify the consequence (financial, regulatory, operational, reputational).

## Countermeasures
- Concrete steps and controls we recommend.

## CTAs
{{< button href="/emergency-assessment" style="primary" >}}🚨 Emergency Threat Assessment →{{< /button >}}
{{< button href="/crisis-hotline" style="ghost" >}}📞 Crisis Response Hotline →{{< /button >}}
{{< button href="/roi-calculator" style="ghost" >}}💰 Calculate Protection ROI →{{< /button >}}

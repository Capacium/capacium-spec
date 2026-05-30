# Proposal to Contribute capability.yaml v1.0 to the Linux Foundation AI & Data

**Date:** 2026-05-11  
**Submitter:** Capacium Project  
**Contact:** typelicious@gmail.com  
**Repository:** https://github.com/Capacium/capacium-spec  
**Spec URL:** https://capacium.xyz/spec/v1.0/schema.json

---

## Executive Summary

We propose contributing the **`capability.yaml` v1.0 open specification** — a vendor-neutral manifest format for AI agent capabilities — to the Linux Foundation AI & Data (LF AI & Data) Foundation as a hosted specification project.

The format is currently used by the Capacium Exchange (a public registry with 300,000+ AI capability listings), the Capacium CLI (`cap`), and 20+ framework adapters. Making this a foundation-governed standard would accelerate ecosystem adoption, ensure vendor neutrality, and provide the trust and stability that enterprise adopters require.

---

## Problem Statement

The AI tooling ecosystem lacks a common manifest format for describing AI capabilities (skills, MCP servers, prompt templates, agent workflows). Today:

- Each AI framework (Claude Desktop, Cursor, Windsurf, VS Code, OpenCode, Gemini CLI, etc.) uses its own format or no manifest at all.
- Capability discovery relies on ad-hoc GitHub topic searches.
- Trust and provenance metadata is completely unstandardized.
- Publishers must create separate manifests for each framework they support.

`capability.yaml` solves this with a single, framework-agnostic manifest that any framework adapter can consume.

---

## What We Are Proposing to Contribute

1. **The `capability.yaml` v1.0 specification** — formal document defining all 11 capability kinds, required/optional fields, trust states, signing conventions, and versioning policy.

2. **JSON Schema Draft 2020-12** — machine-readable schema for automated validation (`schema.json`).

3. **Reference implementations** — open-source validators in Python and Node.js.

4. **Governance model** — proposed working group charter, versioning policy (semver), and deprecation procedures.

---

## Alignment with LF AI & Data Mission

| LF AI & Data Criterion | Capacium Position |
|------------------------|-------------------|
| **Vendor neutrality** | Spec is framework-agnostic; Capacium project holds no IP lock |
| **Open governance** | Proposing WG charter with multi-org representation |
| **Technical merit** | 300k+ real-world capability listings, 20+ framework adapters |
| **Community need** | Active MCP ecosystem (Anthropic, OpenAI, Google) needs shared manifest |
| **Licensing** | Apache 2.0 (spec + schema); MIT (reference implementations) |

---

## Proposed Project Name

**AI Capability Manifest Working Group (ACMWG)**  
Hosted spec: `capability.yaml` / `ai-capability-manifest`

---

## Governance Proposal

### Working Group Charter (Draft)

**Scope:** Define and maintain the `capability.yaml` manifest format and associated JSON Schema for AI capability description, discovery, and installation.

**Non-scope:** Runtime behavior of specific frameworks; registries; package management.

**Decision making:** Lazy consensus with 2/3 supermajority fallback. No single vendor may hold more than 50% of maintainer seats.

**Versioning:** Semantic versioning (MAJOR.MINOR.PATCH). MAJOR = breaking schema change; MINOR = additive fields; PATCH = clarification/errata.

**Deprecation policy:** Minimum 24-month deprecation window for any MAJOR field removal.

**Meeting cadence:** Bi-weekly video call; public GitHub issue tracker; mailing list.

### Initial Proposed Maintainers

| Organization | Proposed Role |
|--------------|---------------|
| Capacium Project | Initial spec author + editor |
| TBD (AI framework vendor) | Co-editor |
| TBD (Enterprise adopter) | Reviewer |
| TBD (Security researcher) | Security reviewer |

We welcome nominations from Anthropic, Google, Microsoft, Cursor, Windsurf, and other MCP-ecosystem participants to fill the co-editor and reviewer seats before formal submission.

---

## IP Contribution

All IP related to the `capability.yaml` specification will be contributed under the **Apache 2.0 License**.  
All reference implementations will be contributed under the **MIT License**.  
No patents are claimed or will be claimed over the format.

The Capacium project commits to transferring the `capacium-spec` GitHub repository to LF AI & Data governance upon project approval.

---

## Current Adoption Metrics (2026-05-11)

| Metric | Value |
|--------|-------|
| Capability listings indexed | 300,000+ |
| Framework adapters | 20+ |
| Capability kinds defined | 11 |
| Reference implementations | Python, Node.js |
| JSON Schema compliance level | Draft 2020-12 |
| Active CLI users (cap) | Growing (telemetry opt-in) |
| Trust states implemented | 4 (discovered → signed) |

---

## Next Steps

1. **LF AI & Data Technical Advisory Council (TAC) review** — submit this proposal to the TAC mailing list.
2. **Incubation application** — complete the LF AI & Data project proposal form.
3. **Working group formation** — identify co-editors from MCP ecosystem vendors.
4. **v1.0 ratification** — adopt current `capability.yaml` v1.0 as the initial standard.
5. **v1.1 roadmap** — incorporate feedback from WG members (first 90-day cycle).

---

## Contact

For questions about this proposal, contact:  
**Capacium Project** · typelicious@gmail.com  
GitHub: https://github.com/Capacium  
Spec: https://github.com/Capacium/capacium-spec

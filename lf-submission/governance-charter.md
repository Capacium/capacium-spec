# AI Capability Manifest Working Group (ACMWG) — Proposed Charter

**Version:** 0.1 (pre-submission draft)  
**Date:** 2026-05-11  
**Status:** Proposed — pending LF AI & Data TAC review

---

## 1. Working Group Name

**AI Capability Manifest Working Group (ACMWG)**

Hosted under: Linux Foundation AI & Data Foundation

---

## 2. Mission

Define and maintain the `capability.yaml` manifest format as an open, vendor-neutral standard for describing, distributing, and governing AI agent capabilities.

---

## 3. Scope

**In scope:**
- The `capability.yaml` YAML schema and semantics
- JSON Schema validation rules
- Capability kind definitions and kind-specific metadata
- Trust state semantics and trust chain rules
- Signing and integrity conventions (Ed25519)
- Versioning and deprecation policy
- Reference implementations (Python, Node.js, and others contributed by WG members)

**Out of scope:**
- Runtime behavior of specific agent frameworks
- Registry protocol, API design, or hosting
- Package installation mechanics
- Billing, entitlement, or SLA commitments

---

## 4. Deliverables

| Deliverable | Target | Cadence |
|-------------|--------|---------|
| Specification document | `capability.yaml` MAJOR.MINOR | As needed |
| JSON Schema | Tracks spec version | Each spec release |
| Reference implementation (Python) | `validator.py` | Each schema change |
| Reference implementation (Node.js) | `validator.js` | Each schema change |
| Test suite | Pass/fail corpus | Each spec release |
| Migration guides | Breaking changes only | MAJOR versions |

---

## 5. Governance

### 5.1 Decision Making

The Working Group operates by **lazy consensus**: a proposal is accepted if no WG member objects within 7 days of posting on the public mailing list.

If consensus cannot be reached, a **2/3 supermajority** of active maintainers (those with ≥ 1 merged PR in the past 180 days) is required to approve a change.

### 5.2 Maintainers

- Minimum 3 maintainers; no single organization may hold > 50% of maintainer seats.
- Maintainers are added by existing maintainer consensus.
- Maintainers inactive for 12+ months may be moved to Emeritus status.

### 5.3 Breaking Changes

Breaking changes (MAJOR version bumps) require:
1. A written proposal (GitHub issue with `breaking-change` label)
2. 30-day public comment period
3. 2/3 maintainer approval
4. Minimum 24-month deprecation window before removing deprecated features

### 5.4 Security Issues

Security vulnerabilities in the specification or reference implementations should be reported to the maintainer list (private) before public disclosure. We follow a 90-day coordinated disclosure policy.

---

## 6. Meetings

- Bi-weekly video call (public, recorded)
- Agenda posted ≥ 48 hours in advance on GitHub
- All decisions logged in meeting notes in the repository

---

## 7. Communication Channels

| Channel | Purpose |
|---------|---------|
| GitHub Issues | Proposals, bugs, questions |
| GitHub Discussions | Community conversation |
| Mailing list | Formal proposals and votes |
| Video call | Working sessions |

---

## 8. Intellectual Property

All contributions to the specification, schema, and reference implementations must be made under the **Developer Certificate of Origin (DCO)** and licensed as follows:

- Specification: **Apache 2.0**
- Reference implementations: **MIT**
- Test corpus: **CC0 1.0**

No patent grants beyond those required by the Apache 2.0 license are made or implied.

---

## 9. Code of Conduct

All participants are expected to abide by the [LF AI & Data Code of Conduct](https://lfai.foundation/about/code-of-conduct/).

---

## 10. Amendment

This charter may be amended by a 2/3 maintainer vote with 14 days notice to the public mailing list.

---

*Proposed charter — subject to LF AI & Data TAC approval.*

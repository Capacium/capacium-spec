# AI Capability Manifest Specification v1.0

**Specification Identifier:** `ai-capability-manifest`  
**Version:** 1.0.0  
**Status:** Proposed Standard  
**Published:** 2026-05-11  
**Working Group:** AI Capability Manifest WG (ACMWG) — proposed  
**Repository:** https://github.com/Capacium/capacium-spec  
**Schema:** https://capacium.xyz/spec/v1.0/schema.json  
**License:** Apache 2.0

---

## Notice

Copyright 2026, Capacium Project contributors. All Rights Reserved.

This specification is made available under the Apache License, Version 2.0. You may obtain a copy at http://www.apache.org/licenses/LICENSE-2.0

THIS SPECIFICATION IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Terminology](#2-terminology)
3. [Capability Manifest Structure](#3-capability-manifest-structure)
4. [Required Fields](#4-required-fields)
5. [Optional Fields](#5-optional-fields)
6. [Capability Kinds](#6-capability-kinds)
7. [Kind-Specific Metadata](#7-kind-specific-metadata)
8. [Trust States](#8-trust-states)
9. [Signing Convention](#9-signing-convention)
10. [Versioning Policy](#10-versioning-policy)
11. [Conformance](#11-conformance)
12. [Security Considerations](#12-security-considerations)
13. [IANA Considerations](#13-iana-considerations)
14. [Appendix A — JSON Schema](#14-appendix-a--json-schema)
15. [Appendix B — Examples](#15-appendix-b--examples)

---

## 1. Introduction

### 1.1 Purpose

The **AI Capability Manifest** (`capability.yaml`) is an open, vendor-neutral format for describing AI agent capabilities. A capability is a self-describing, installable unit of functionality that can be discovered, installed, and composed across AI agent frameworks.

This specification defines the structure, semantics, and validation rules for `capability.yaml` v1.0 manifests.

### 1.2 Background

The AI tooling ecosystem includes dozens of agent frameworks (Claude Desktop, Cursor, Windsurf, VS Code with Copilot, OpenCode, Gemini CLI, and others) and a rapidly growing set of reusable capabilities (skills, MCP servers, prompt templates, workflows). Without a shared manifest format, capability distribution is fragmented, discovery is unreliable, and trust provenance is absent.

`capability.yaml` addresses this by providing a single, framework-agnostic manifest that:

- Describes what a capability does
- Declares how it should be installed
- Establishes a machine-verifiable trust chain
- Enables cross-registry discovery

### 1.3 Scope

This specification covers:

- The `capability.yaml` manifest format
- All 11 capability kinds and their kind-specific metadata schemas
- Trust state semantics
- Ed25519 signing conventions
- Versioning and deprecation policy
- Conformance requirements for validators and registries

This specification does NOT cover:

- Runtime behavior of specific frameworks
- Registry protocol or API design
- Installation mechanics (handled by clients)
- Billing or entitlement

### 1.4 Relationship to Other Standards

| Standard | Relationship |
|----------|-------------|
| MCP (Model Context Protocol) | `mcp-server` kind wraps MCP servers; this spec is a superset |
| SPDX | `license` field uses SPDX identifiers |
| semver 2.0.0 | `version` field MUST be semver-compliant |
| JSON Schema Draft 2020-12 | Machine-readable validation schema |
| Ed25519 (RFC 8032) | Signing convention |

---

## 2. Terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

| Term | Definition |
|------|-----------|
| **Capability** | An installable unit of AI agent functionality described by a `capability.yaml` manifest |
| **Kind** | The type classification of a capability (e.g. `skill`, `mcp-server`, `bundle`) |
| **Publisher** | An entity (person or organization) that publishes capabilities to a registry |
| **Registry** | A service that indexes, stores, and serves capability manifests |
| **Trust state** | A machine-readable trust level assigned to a capability by a registry or auditor |
| **Framework adapter** | Software that installs a capability into a specific agent framework |
| **Canonical name** | The globally unique `owner/capability-name` identifier |

---

## 3. Capability Manifest Structure

A `capability.yaml` file MUST be a valid YAML 1.2 document containing a single mapping (dictionary) at the root level.

### 3.1 Filename

The primary manifest filename SHOULD be `capability.yaml`. Implementations MAY also accept `capability.yml`.

### 3.2 Encoding

Manifest files MUST be encoded in UTF-8 without BOM.

### 3.3 YAML version

Manifests MUST be parseable as YAML 1.1 or YAML 1.2.

---

## 4. Required Fields

The following fields are REQUIRED in every `capability.yaml`:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `name` | string | Pattern: `^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-z0-9][a-z0-9-]*$` | Canonical name: `owner/capability-name` |
| `version` | string | semver 2.0.0 | Semantic version |
| `kind` | string | Enum (see §6) | Capability kind |
| `description` | string | ≤ 200 chars RECOMMENDED | Short human-readable description |

### 4.1 name

The `name` field MUST follow the pattern `owner/capability-name` where:

- `owner` is one or more alphanumeric, dot, hyphen, or underscore characters
- `capability-name` is one or more lowercase alphanumeric or hyphen characters

Examples: `acme-corp/code-reviewer`, `anthropic/research-assistant`

### 4.2 version

The `version` field MUST be a valid [Semantic Versioning 2.0.0](https://semver.org) string.

`0.0.0` is RESERVED and MUST NOT be used for published capabilities.

### 4.3 kind

See §6 for the complete enumeration of valid kinds.

### 4.4 description

Short description of the capability. SHOULD be ≤ 200 characters. Extended descriptions belong in `long_description`.

---

## 5. Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `long_description` | string | Extended Markdown description |
| `canonical_source_url` | string (URI) | Canonical source repository URL |
| `license` | string | SPDX identifier (e.g. `MIT`, `Apache-2.0`) |
| `tags` | list[string] | Searchable tags |
| `frameworks` | list[string] | Target framework identifiers |
| `runtimes` | object | Runtime version constraints (e.g. `{uv: ">=0.4.0"}`) |
| `dependencies` | list[object] | Capability dependencies: `[{name, version_constraint}]` |
| `entry_points` | list[object] | Entry point definitions |
| `assets` | list[object] | Linked assets |
| `signature` | object | Ed25519 signature (see §9) |
| `trust_state` | string | Publisher-declared trust state hint (registry may override) |

---

## 6. Capability Kinds

The `kind` field MUST be one of the following values:

| Kind | Description |
|------|-------------|
| `skill` | Self-contained, single-purpose capability |
| `mcp-server` | MCP (Model Context Protocol) server exposing tools |
| `bundle` | Named collection of capabilities |
| `tool` | Standalone callable tool (function/CLI) |
| `prompt` | Prompt template or system prompt |
| `template` | Project or file scaffold template |
| `workflow` | Multi-step agent workflow |
| `connector-pack` | Collection of API connectors |
| `operator` | Human-in-the-loop operator capability (Work 5.0) |
| `checkpoint` | Human review checkpoint in an agent pipeline (Work 5.0) |
| `policy` | Policy-as-code rules for capability governance (Work 5.0) |
| `resource` | Non-executable resource asset (prompt library, dataset, config template, model weights, tool index, embedding) — see `resource_type` |

New kinds MAY be added in MINOR versions. Validators MUST NOT reject manifests with unrecognized kinds (they SHOULD emit a warning).

---

## 7. Kind-Specific Metadata

### 7.1 mcp-server: `mcp_meta`

RECOMMENDED for `kind: mcp-server`.

```yaml
mcp_meta:
  transport: stdio          # stdio | http | sse
  tools:                    # list of tool names exposed
    - name: read_file
      description: "Read a file from disk"
  resources: []             # optional MCP resources
  prompts: []               # optional MCP prompts
```

### 7.2 bundle: `bundle_meta`

RECOMMENDED for `kind: bundle`.

```yaml
bundle_meta:
  capabilities:
    - owner/skill-a@1.0.0
    - owner/mcp-server-b@2.1.0
```

### 7.3 operator: `operator_meta`

REQUIRED for `kind: operator`.

```yaml
operator_meta:
  role: "code-reviewer"          # free-form role label
  sla_hours: 4                   # expected response time in hours
  approval_modes:                # supported interaction modes
    - async-email
    - slack-thread
  escalation_path: "owner/escalation-operator"  # optional fallback
```

### 7.4 checkpoint: `checkpoint_meta`

REQUIRED for `kind: checkpoint`.

```yaml
checkpoint_meta:
  fallback: reject               # approve | reject | escalate
  timeout_hours: 24              # time before fallback triggers
  reviewers:                     # optional reviewer identifiers
    - github:acme-security-team
```

### 7.5 policy: `policy_meta`

REQUIRED for `kind: policy`.

```yaml
policy_meta:
  minimum_trust_state: audited          # discovered | audited | verified | signed
  allowed_publishers: []                # empty = allow all
  blocked_kinds: [workflow]             # empty = block none
  blocked_capabilities: []             # explicit deny list
  require_license: true
  min_quality_score: 60
```

---

## 8. Trust States

Trust states form a monotonically increasing chain. A registry MAY promote capabilities to higher trust states and MUST NOT demote without cause.

| State | Description | Criteria |
|-------|-------------|----------|
| `discovered` | Auto-indexed from public source | Exists and is parseable |
| `audited` | Human or automated audit completed | Passes static analysis + schema |
| `verified` | Publisher identity verified | Verified GitHub org + OIDC |
| `signed` | Ed25519-signed by publisher | Valid signature present |

### 8.1 Trust State Transitions

Valid transitions (in order): `discovered` → `audited` → `verified` → `signed`

Reverse transitions MUST be accompanied by a `revocation_reason` and recorded in the registry audit log.

---

## 9. Signing Convention

Capabilities MAY be signed using Ed25519 (RFC 8032).

```yaml
signature:
  public_key: "base64url-encoded-ed25519-public-key"
  value: "base64url-encoded-ed25519-signature"
  signed_fields: ["name", "version", "kind", "description"]
  algorithm: "Ed25519"
```

### 9.1 Signing procedure

1. Collect the values of all `signed_fields` in the order listed.
2. Serialize to UTF-8 JSON: `{"name": "...", "version": "...", ...}`.
3. Compute Ed25519 signature over the UTF-8 bytes.
4. Base64url-encode (no padding) the signature and public key.

Validators MUST verify signatures when the `signature` block is present and `trust_state` is `signed`.

---

## 10. Versioning Policy

### 10.1 Specification versioning

This specification uses Semantic Versioning 2.0.0:

- **MAJOR**: Breaking changes to required fields or kind semantics
- **MINOR**: New optional fields, new kinds, clarifications
- **PATCH**: Errata, non-normative editorial changes

### 10.2 Capability versioning

Capability `version` fields MUST use Semantic Versioning 2.0.0.

### 10.3 Deprecation

Fields or kinds marked deprecated MUST be retained for a minimum of **24 months** after the deprecation announcement before removal in a MAJOR version.

---

## 11. Conformance

### 11.1 Conformant manifest

A `capability.yaml` file is **conformant** if it:

1. Contains all required fields (§4)
2. Has a valid `kind` value (§6) or a `kind` not in the enum (warning, not error)
3. Has a `version` that is valid semver
4. Has a `name` matching the `owner/capability-name` pattern
5. If kind-specific metadata is required (§7), that metadata is present and valid
6. If a `signature` block is present, it is structurally valid

### 11.2 Conformant validator

A validator is **conformant** if it:

1. Reports all required-field violations as errors
2. Reports unrecognized kinds as warnings (not errors)
3. Validates kind-specific metadata when present
4. Verifies Ed25519 signatures when `signature.value` is present
5. Returns exit code 0 on valid, non-zero on invalid

### 11.3 Conformant registry

A registry is **conformant** if it:

1. Accepts all conformant manifests
2. Rejects manifests with invalid `name` format or invalid semver
3. Stores and exposes trust state per §8
4. Does not modify publisher-submitted manifest fields (may add registry-derived metadata)

---

## 12. Security Considerations

### 12.1 Supply chain

- Registries SHOULD verify publisher identity before assigning `verified` or `signed` trust state.
- Clients SHOULD check trust state before installing capabilities in production.
- Policy enforcement (§7.5) enables organizations to define minimum trust requirements.

### 12.2 Dependency confusion

The `name` format (`owner/capability-name`) prevents dependency confusion attacks by requiring explicit owner qualification.

### 12.3 Signature verification

Clients SHOULD verify Ed25519 signatures for `trust_state: signed` capabilities. Signature verification failures MUST be reported to the user.

### 12.4 YAML parsing

Validators MUST use `yaml.safe_load()` or equivalent safe YAML parsing. Arbitrary YAML tags and Python object construction MUST be rejected.

---

## 13. IANA Considerations

This specification requests no IANA actions.

The MIME type `application/vnd.capacium.capability+yaml` is proposed for `capability.yaml` content when transmitted over HTTP (informational, not yet registered).

---

## 14. Appendix A — JSON Schema

The normative JSON Schema (Draft 2020-12) for `capability.yaml` v1.0 is maintained at:

```
https://capacium.xyz/spec/v1.0/schema.json
```

A cached copy is distributed with the reference implementations. In case of conflict between this document and the JSON Schema, this document takes precedence.

---

## 15. Appendix B — Examples

### B.1 Minimal skill

```yaml
name: acme-corp/hello-world
version: 1.0.0
kind: skill
description: "A hello world skill for testing."
```

### B.2 MCP server

```yaml
name: acme-corp/filesystem-mcp
version: 2.1.0
kind: mcp-server
description: "MCP server for local filesystem access."
license: MIT
canonical_source_url: https://github.com/acme-corp/filesystem-mcp
frameworks: [claude-code, cursor, windsurf]
mcp_meta:
  transport: stdio
  tools:
    - name: read_file
      description: "Read a file from disk"
    - name: write_file
      description: "Write content to a file"
    - name: list_directory
      description: "List directory contents"
```

### B.3 Policy

```yaml
name: acme-corp/enterprise-policy
version: 1.0.0
kind: policy
description: "Enterprise capability policy for ACME Corp deployments."
policy_meta:
  minimum_trust_state: audited
  allowed_publishers: ["acme-corp", "trusted-vendor"]
  blocked_kinds: ["workflow"]
  require_license: true
  min_quality_score: 60
```

### B.4 Bundle

```yaml
name: acme-corp/dev-bundle
version: 1.5.0
kind: bundle
description: "Standard developer toolset for ACME projects."
bundle_meta:
  capabilities:
    - acme-corp/code-reviewer@2.0.0
    - acme-corp/filesystem-mcp@2.1.0
    - acme-corp/test-runner@1.0.0
```

---

*End of specification.*

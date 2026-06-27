# capability.yaml v1.0 Formal Specification

**Version:** 1.0.0  
**Status:** Draft  
**Published:** 2026-05-11  
**Repository:** https://github.com/Capacium/capacium-spec  
**Schema:** https://capacium.xyz/spec/v1.0/schema.json  
**Maintainer:** fusionAIze (fusionaize.com)

---

## Abstract

`capability.yaml` is an open, vendor-neutral format for describing AI capabilities — units of functionality that can be discovered, installed, and composed across AI agent frameworks. This document defines the v1.0 formal specification, including required and optional fields, all capability kinds, versioning semantics, trust states, and signing conventions.

---

## 1. Overview

A capability is a self-describing, installable package of functionality for AI agents. The `capability.yaml` manifest describes what a capability does, what kind it is, and how to install and use it. The Capacium CLI (`cap`) consumes this manifest to install, validate, and manage capabilities.

### 1.1 Design goals

1. **Human-readable**: YAML, not JSON. Comments allowed.
2. **Backward compatible**: All v0.x `capability.yaml` files pass v1.0 validation.
3. **Kind-extensible**: New kinds can be added without breaking existing validators.
4. **Trust-first**: Trust state is a first-class field, not a registry implementation detail.
5. **Framework-agnostic**: Works with Claude Desktop, Cursor, Windsurf, VS Code, and 20+ adapters.

---

## 2. Capability Kinds

The `kind` field identifies the type of capability. All kinds are lowercase strings.

| Kind | Description | Primary Audience |
|------|-------------|-----------------|
| `skill` | A self-contained, single-purpose capability (function, script, or package) | All agents |
| `mcp-server` | An MCP (Model Context Protocol) server that exposes tools via stdio/HTTP | Claude, Cursor, Windsurf |
| `bundle` | A named collection of skills, mcp-servers, and/or other bundles | Publishers |
| `tool` | A reusable function or utility (lighter than a full skill) | All agents |
| `prompt` | A prompt template or system prompt package | All agents |
| `template` | A project template or starter kit | Developers |
| `workflow` | A multi-step automated workflow (e.g. GitHub Action) | CI/CD systems |
| `connector-pack` | A collection of API connectors | Enterprise |
| `operator` | A human-in-the-loop step in an agent workflow (Work 5.0) | Enterprise operators |
| `checkpoint` | An automated or human-approval gate in an agent pipeline | Enterprise |
| `policy` | Declarative policy governing capability usage (Work 5.0) | Enterprise |
| `resource` | A non-executable resource asset (prompt library, dataset, config template, model weights, tool index, embedding) — see `resource_type` | All agents |

---

## 3. Required Fields

Every `capability.yaml` MUST contain all four required fields:

```yaml
name: owner/my-capability
version: 1.0.0
kind: skill
description: A one-line description of what this capability does.
```

### 3.1 `name`

**Type:** string  
**Format:** `owner/capability-name` (slash-separated)  
**Constraints:**
- MUST be globally unique within the registry
- Owner MUST be a valid GitHub username or org name
- Capability name MUST match pattern `[a-z0-9][a-z0-9-]*`
- Maximum length: 128 characters total

**Examples:**
```yaml
name: typelicious/pdf-extractor
name: acme-corp/crm-connector
```

### 3.2 `version`

**Type:** string  
**Format:** Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH[-prerelease][+build]`)  
**Constraints:** MUST be a valid semver string

**Versioning policy:**
- `MAJOR`: breaking changes to the public interface (tool names, input schemas, output format)
- `MINOR`: backward-compatible new features (new tools, new optional fields)
- `PATCH`: bug fixes and documentation updates

**Examples:**
```yaml
version: 1.0.0
version: 2.3.1-beta.1
version: 0.9.0
```

### 3.3 `kind`

**Type:** string  
**Format:** Enumerated — see Section 2  
**Constraints:** MUST be one of the 11 defined kinds

### 3.4 `description`

**Type:** string  
**Constraints:**
- MUST be present and non-empty
- SHOULD be one sentence (≤ 200 characters)
- MUST be in English (additional languages via `description_i18n`)

---

## 4. Optional Fields

### 4.1 General optional fields

```yaml
# Source repository URL
canonical_source_url: https://github.com/owner/repo

# SPDX license identifier
license: MIT

# Searchable tags (lowercase, hyphenated)
tags:
  - pdf
  - document-processing
  - extraction

# Primary category
category: developer-tools

# Target AI agent frameworks
frameworks:
  - claude-code
  - cursor
  - windsurf
  - opencode
  - gemini-cli

# Runtime requirements
runtimes:
  python: ">=3.10"
  node: ">=20"
  uv: ">=0.4.0"

# Dependencies on other capabilities
dependencies:
  - name: typelicious/base-utils
    version: ">=1.0.0"
    kind: skill

# Long-form description (Markdown)
long_description: |
  This capability extracts text, tables, and metadata from PDF files
  using a combination of pdfplumber and pytesseract for OCR fallback.

# Internationalized descriptions
description_i18n:
  ja: "PDFファイルからテキストと表を抽出します"
  zh: "从PDF文件中提取文本和表格"
  de: "Extrahiert Text und Tabellen aus PDF-Dateien"
```

### 4.2 `mcp_meta` (required for `kind: mcp-server`)

When `kind: mcp-server`, the `mcp_meta` block describes the tools exposed:

```yaml
kind: mcp-server
mcp_meta:
  transport: stdio          # stdio | http | sse
  command: python           # command to start the server (for stdio)
  args: ["-m", "my_mcp_server"]
  env:                      # required environment variables
    - name: API_KEY
      required: true
      description: "API key for the underlying service"
  tools:
    - name: extract_pdf_text
      description: "Extract all text from a PDF file"
      input_schema:
        type: object
        properties:
          file_path:
            type: string
            description: "Absolute path to the PDF file"
        required: [file_path]
    - name: extract_pdf_tables
      description: "Extract tabular data from a PDF file as JSON"
```

### 4.3 `bundle_meta` (required for `kind: bundle`)

```yaml
kind: bundle
bundle_meta:
  capabilities:
    - name: typelicious/pdf-extractor
      version: ">=1.0.0"
    - name: typelicious/doc-converter
      version: "~1.2.0"
  install_all: true        # install all on cap install
```

### 4.4 `operator_meta` (required for `kind: operator`)

```yaml
kind: operator
operator_meta:
  role: legal-reviewer
  sla_hours: 24
  approval_modes:
    - approve
    - reject
    - request-changes
  notification: email
  escalation_to: manager    # role to escalate to if SLA exceeded
```

### 4.5 `checkpoint_meta` (required for `kind: checkpoint`)

```yaml
kind: checkpoint
checkpoint_meta:
  automated_check: security-scanner-result
  escalation_to: human-review
  timeout_hours: 4
  fallback: reject          # approve | reject | escalate
  conditions:
    - field: trust_state
      operator: gte
      value: verified
```

### 4.6 `policy_meta` (required for `kind: policy`)

```yaml
kind: policy
policy_meta:
  minimum_trust_state: verified   # discovered | audited | verified | signed
  allowed_publishers:
    - anthropics
    - typelicious
  blocked_kinds:
    - mcp-server
  require_audit_log: true
  max_capability_age_days: 365
```

---

## 5. Trust States

Trust states are assigned by the Capacium Exchange registry, not by publishers. They form a monotonically increasing chain.

| State | Description | Requirements |
|-------|-------------|-------------|
| `discovered` | Found by crawler or publisher-submitted | Canonical name + kind present |
| `audited` | Basic quality checks passed | quality_score ≥ 40 |
| `verified` | Deep validation passed | quality_score ≥ 70 + source verified |
| `signed` | Publisher Ed25519-signed | Ed25519 signature present and valid |

### 5.1 Trust in capability.yaml

Publishers MUST NOT set `trust_state` in their `capability.yaml`. The registry assigns trust state. Including it in the manifest is silently ignored.

---

## 6. Signing

Capabilities can be signed using Ed25519 (ECDSA over Curve25519).

```yaml
# These fields are set by the Exchange, not by publishers
signature:
  public_key: "ed25519:base64url-encoded-public-key"
  value: "base64url-encoded-signature"
  signed_by: "publisher-key-id"
  signed_at: "2026-05-11T00:00:00Z"
```

### 6.1 What is signed

The signature covers: `canonical_name + "|" + version` encoded as UTF-8.

### 6.2 Verification

```python
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import load_der_public_key

def verify_capability_signature(canonical_name: str, version: str,
                                 public_key_b64: str, signature_b64: str) -> bool:
    message = f"{canonical_name}|{version}".encode("utf-8")
    pub_key_bytes = base64.urlsafe_b64decode(public_key_b64 + "==")
    sig_bytes = base64.urlsafe_b64decode(signature_b64 + "==")
    try:
        pubkey = Ed25519PublicKey.from_public_bytes(pub_key_bytes)
        pubkey.verify(sig_bytes, message)
        return True
    except Exception:
        return False
```

---

## 7. Versioning Policy

### 7.1 v1.0 backward compatibility

All v0.x `capability.yaml` files MUST pass v1.0 validation. The v1.0 validator:
1. Accepts any `kind` that matches the 11 defined kinds plus any unknown kind (warns but does not reject)
2. `version: "0.0.0"` is accepted (warning issued)
3. Unknown top-level keys are ignored
4. Missing `canonical_source_url` is allowed (warning only)

### 7.2 Future versions

Future spec versions (v1.1, v2.0) MUST declare their schema at:
`https://capacium.xyz/spec/v{MAJOR}.{MINOR}/schema.json`

---

## 8. Complete Example

```yaml
# capability.yaml v1.0
# Schema: https://capacium.xyz/spec/v1.0/schema.json

name: typelicious/pdf-extractor
version: 1.2.0
kind: mcp-server
description: "Extract text, tables, and metadata from PDF files via MCP tools."

canonical_source_url: https://github.com/typelicious/pdf-extractor
license: MIT
tags:
  - pdf
  - document-processing
  - extraction
  - ocr

category: developer-tools

frameworks:
  - claude-code
  - cursor
  - windsurf

runtimes:
  python: ">=3.10"
  uv: ">=0.4.0"

mcp_meta:
  transport: stdio
  command: python
  args: ["-m", "pdf_extractor.server"]
  env:
    - name: TESSERACT_PATH
      required: false
      description: "Path to Tesseract binary for OCR fallback"
  tools:
    - name: extract_text
      description: "Extract all text from a PDF file"
    - name: extract_tables
      description: "Extract tables as JSON arrays"
    - name: get_metadata
      description: "Get PDF metadata (author, title, pages)"
```

---

## 9. JSON Schema Location

The machine-readable JSON Schema for this specification is published at:

```
https://capacium.xyz/spec/v1.0/schema.json
```

The schema can be used in any JSON Schema validator (Draft 2020-12 compatible).

To validate locally:
```bash
pip install jsonschema pyyaml
cap validate capability.yaml
```

---

## 10. Governance

This specification is maintained by the Capacium Project. Proposed changes:
1. Open a GitHub Issue in `Capacium/capacium-spec`
2. 14-day comment period
3. Merge requires approval from 2 maintainers

Submission to the Linux Foundation AI & Data Foundation working group is in progress (see `lf-submission/` in this repository).

---

*Copyright 2026 Capacium Project contributors. Licensed under CC BY 4.0.*

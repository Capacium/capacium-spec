# Capacium Capability Specification

> [!NOTE]
> **Public mirror.** The canonical repository is hosted on our self-hosted git.
> This GitHub copy is a read-only mirror kept in sync for visibility. Bug
> reports are welcome via Issues; pull requests are applied upstream and synced
> back here.

**Version 1.0 (Draft)** · Specification: **Apache-2.0** · Reference implementations: **MIT**

The formal specification for **`capability.yaml`** — the manifest format that
describes AI-agent capabilities (skills, MCP servers, tools, prompts, templates,
workflows, resources, bundles, connector-packs) in the Capacium ecosystem.
A single, portable descriptor any agent framework can read.

## Contents

| Path | What |
|------|------|
| [`spec/v1.0/capability-spec.md`](spec/v1.0/capability-spec.md) | The formal specification |
| [`spec/v1.0/schema.json`](spec/v1.0/schema.json) | JSON Schema (also at `https://capacium.xyz/spec/v1.0/schema.json`) |
| [`examples/`](examples/) | Example manifests — `skill`, `mcp-server`, `resource`, `bundle` |
| [`reference-implementations/`](reference-implementations/) | Reference parsers/validators (Node + Python) |
| [`lf-submission/`](lf-submission/) | Open-governance materials (charter, cover letter) |

## Status

`v1.0` is a **Draft** — the format and schema may still change. Governance
materials for an open, vendor-neutral home are prepared under
[`lf-submission/`](lf-submission/).

## License & Governance

- **Specification** (`spec/`): Apache-2.0
- **Reference implementations** (`reference-implementations/`): MIT
- All contributions are made under the **Developer Certificate of Origin (DCO)**.
- Governance: see [`lf-submission/governance-charter.md`](lf-submission/governance-charter.md).

## Maintainer

**fusionAIze** · [fusionaize.com](https://fusionaize.com)

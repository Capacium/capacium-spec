#!/usr/bin/env python3
"""capability.yaml v1.0 Reference Validator — Python implementation.

Usage:
    from validator import validate
    result = validate("capability.yaml")
    print(result)  # {"valid": True, "errors": [], "warnings": [...]}

Or as CLI:
    python validator.py capability.yaml
    python validator.py capability.yaml --strict
    python validator.py capability.yaml --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

try:
    import jsonschema
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

SCHEMA_URL = "https://capacium.xyz/spec/v1.0/schema.json"
SCHEMA_CACHE_DIR = Path.home() / ".capacium" / "cache"
SCHEMA_CACHE_PATH = SCHEMA_CACHE_DIR / "spec-v1.0-schema.json"

VALID_KINDS = {
    "skill", "mcp-server", "bundle", "tool", "prompt",
    "template", "workflow", "connector-pack",
    "operator", "checkpoint", "policy", "resource",
}

TRUST_STATES = ["discovered", "audited", "verified", "signed"]

SEMVER_RE = re.compile(
    r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
    r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)

NAME_RE = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*/[a-z0-9][a-z0-9-]*$')


def _fetch_schema() -> Optional[Dict[str, Any]]:
    """Fetch schema from cache or remote."""
    if SCHEMA_CACHE_PATH.exists():
        try:
            return json.loads(SCHEMA_CACHE_PATH.read_text())
        except Exception:
            pass
    try:
        req = urllib.request.Request(
            SCHEMA_URL,
            headers={"User-Agent": "capacium-spec-validator/1.0"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            schema_text = r.read().decode()
        SCHEMA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        SCHEMA_CACHE_PATH.write_text(schema_text)
        return json.loads(schema_text)
    except Exception:
        return None


def _semantic_checks(data: Dict[str, Any], strict: bool) -> tuple[List[str], List[str]]:
    """Run semantic checks beyond JSON Schema.

    Returns (errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    name = data.get("name", "")
    version = data.get("version", "")
    kind = data.get("kind", "")

    # Name format
    if name and not NAME_RE.match(name):
        errors.append(
            f"name '{name}' must match pattern 'owner/capability-name' "
            f"(owner: alphanumeric+._-, name: lowercase alphanumeric+hyphen)"
        )

    # Version
    if version:
        if not SEMVER_RE.match(version):
            errors.append(
                f"version '{version}' is not a valid semver string "
                f"(e.g. 1.0.0, 2.3.1-beta.1)"
            )
        elif version == "0.0.0":
            warnings.append("version '0.0.0' should be updated to a real version")

    # Kind-specific checks
    if kind == "mcp-server" and "mcp_meta" not in data:
        warnings.append("kind 'mcp-server' should include a 'mcp_meta' block with tools list")

    if kind == "bundle" and "bundle_meta" not in data:
        warnings.append("kind 'bundle' should include a 'bundle_meta' block with capabilities list")

    if kind == "operator" and "operator_meta" not in data:
        errors.append("kind 'operator' requires an 'operator_meta' block")

    if kind == "checkpoint" and "checkpoint_meta" not in data:
        errors.append("kind 'checkpoint' requires a 'checkpoint_meta' block")

    if kind == "policy" and "policy_meta" not in data:
        errors.append("kind 'policy' requires a 'policy_meta' block")

    # Description length
    desc = data.get("description", "")
    if len(desc) > 200:
        warnings.append(
            f"description is {len(desc)} chars (recommended: ≤ 200). "
            f"Use 'long_description' for extended text."
        )

    # Strict mode: recommended fields
    if strict:
        if not data.get("canonical_source_url"):
            warnings.append("--strict: no 'canonical_source_url' set")
        if not data.get("license"):
            warnings.append("--strict: no 'license' field (use SPDX identifier e.g. MIT)")
        if not data.get("tags"):
            warnings.append("--strict: no 'tags' — improves discoverability")
        if not data.get("frameworks"):
            warnings.append("--strict: no 'frameworks' — specify target agent frameworks")

    return errors, warnings


def validate(
    path: str,
    strict: bool = False,
    use_remote_schema: bool = True,
) -> Dict[str, Any]:
    """Validate a capability.yaml file against the v1.0 spec.

    Args:
        path: Path to capability.yaml file
        strict: If True, also check recommended fields
        use_remote_schema: If True, fetch JSON Schema for additional validation

    Returns:
        dict with keys: valid (bool), errors (list), warnings (list),
                        name (str), kind (str), version (str)
    """
    p = Path(path)

    if not p.exists():
        return {
            "valid": False,
            "errors": [f"File not found: {path}"],
            "warnings": [],
            "name": "",
            "kind": "",
            "version": "",
        }

    # Parse YAML
    if not _HAS_YAML:
        return {
            "valid": False,
            "errors": ["PyYAML not installed — run: pip install pyyaml"],
            "warnings": [],
            "name": "",
            "kind": "",
            "version": "",
        }

    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"YAML parse error: {e}"],
            "warnings": [],
            "name": "",
            "kind": "",
            "version": "",
        }

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["capability.yaml must be a YAML mapping (dict), not a list or scalar"],
            "warnings": [],
            "name": "",
            "kind": "",
            "version": "",
        }

    errors: List[str] = []
    warnings: List[str] = []

    # Required fields
    for field in ("name", "version", "kind", "description"):
        if field not in data or not data[field]:
            errors.append(f"Required field missing or empty: '{field}'")

    # JSON Schema validation
    if use_remote_schema and _HAS_JSONSCHEMA and not errors:
        schema = _fetch_schema()
        if schema:
            v = jsonschema.Draft202012Validator(schema)
            for err in v.iter_errors(data):
                errors.append(f"Schema: {err.message} (at {'.'.join(str(p) for p in err.path) or 'root'})")

    # Semantic checks
    sem_errors, sem_warnings = _semantic_checks(data, strict)
    errors.extend(sem_errors)
    warnings.extend(sem_warnings)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "name": data.get("name", ""),
        "kind": data.get("kind", ""),
        "version": data.get("version", ""),
    }


def _print_human(result: Dict[str, Any], path: str) -> None:
    """Print human-readable validation output."""
    if result["valid"]:
        print(f"✅  {path} is valid (capability.yaml v1.0)")
        if result.get("name"):
            print(f"    Name:    {result['name']}")
        if result.get("kind"):
            print(f"    Kind:    {result['kind']}")
        if result.get("version"):
            print(f"    Version: {result['version']}")
    else:
        print(f"❌  {path} is INVALID")
        for err in result["errors"]:
            print(f"    ERROR: {err}")

    if result.get("warnings"):
        print(f"    Warnings ({len(result['warnings'])}):")
        for w in result["warnings"]:
            print(f"      ⚠️  {w}")
    elif result["valid"]:
        print(f"    Issues:  None")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate a capability.yaml file against the v1.0 specification",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="capability.yaml",
        help="Path to capability.yaml (default: ./capability.yaml)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also check recommended fields (canonical_source_url, license, tags, frameworks)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output result as JSON",
    )
    parser.add_argument(
        "--no-schema",
        action="store_true",
        help="Skip remote JSON Schema validation (offline mode)",
    )
    args = parser.parse_args()

    result = validate(
        args.path,
        strict=args.strict,
        use_remote_schema=not args.no_schema,
    )

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result, args.path)

    sys.exit(0 if result["valid"] else 1)

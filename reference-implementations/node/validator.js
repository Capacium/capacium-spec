#!/usr/bin/env node
/**
 * capability.yaml v1.0 Reference Validator — Node.js implementation
 *
 * Usage:
 *   const { validate } = require('./validator');
 *   const result = await validate('capability.yaml');
 *   console.log(result); // { valid: true, errors: [], warnings: [...] }
 *
 * CLI:
 *   node validator.js capability.yaml
 *   node validator.js capability.yaml --strict
 *   node validator.js capability.yaml --json
 */

'use strict';

const fs = require('fs');
const https = require('https');
const http = require('http');
const path = require('path');
const os = require('os');

// Optional dependencies (install with: npm install js-yaml ajv)
let yaml, Ajv;
try { yaml = require('js-yaml'); } catch {}
try { const AjvLib = require('ajv/dist/2020'); Ajv = AjvLib; } catch {}

const SCHEMA_URL = 'https://capacium.xyz/spec/v1.0/schema.json';
const SCHEMA_CACHE_PATH = path.join(os.homedir(), '.capacium', 'cache', 'spec-v1.0-schema.json');

const VALID_KINDS = new Set([
  'skill', 'mcp-server', 'bundle', 'tool', 'prompt',
  'template', 'workflow', 'connector-pack',
  'operator', 'checkpoint', 'policy', 'resource',
]);

const SEMVER_RE = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$/;
const NAME_RE = /^[a-zA-Z0-9][a-zA-Z0-9._-]*\/[a-z0-9][a-z0-9-]*$/;

/**
 * Fetch URL and return body as string. Returns null on error.
 */
function fetchUrl(url) {
  return new Promise((resolve) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { timeout: 5000 }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => resolve(data));
    });
    req.on('error', () => resolve(null));
    req.on('timeout', () => { req.destroy(); resolve(null); });
  });
}

async function fetchSchema() {
  try {
    if (fs.existsSync(SCHEMA_CACHE_PATH)) {
      return JSON.parse(fs.readFileSync(SCHEMA_CACHE_PATH, 'utf8'));
    }
  } catch {}
  const body = await fetchUrl(SCHEMA_URL);
  if (!body) return null;
  try {
    const schema = JSON.parse(body);
    const cacheDir = path.dirname(SCHEMA_CACHE_PATH);
    fs.mkdirSync(cacheDir, { recursive: true });
    fs.writeFileSync(SCHEMA_CACHE_PATH, body);
    return schema;
  } catch {
    return null;
  }
}

function semanticChecks(data, strict) {
  const errors = [];
  const warnings = [];

  const { name = '', version = '', kind = '' } = data;

  if (name && !NAME_RE.test(name)) {
    errors.push(
      `name '${name}' must match pattern 'owner/capability-name' ` +
      `(owner: alphanumeric+._-, name: lowercase alphanumeric+hyphen)`
    );
  }

  if (version) {
    if (!SEMVER_RE.test(version)) {
      errors.push(`version '${version}' is not a valid semver string (e.g. 1.0.0, 2.3.1-beta.1)`);
    } else if (version === '0.0.0') {
      warnings.push("version '0.0.0' should be updated to a real version");
    }
  }

  if (kind === 'mcp-server' && !data.mcp_meta) {
    warnings.push("kind 'mcp-server' should include a 'mcp_meta' block with tools list");
  }
  if (kind === 'bundle' && !data.bundle_meta) {
    warnings.push("kind 'bundle' should include a 'bundle_meta' block with capabilities list");
  }
  if (kind === 'operator' && !data.operator_meta) {
    errors.push("kind 'operator' requires an 'operator_meta' block");
  }
  if (kind === 'checkpoint' && !data.checkpoint_meta) {
    errors.push("kind 'checkpoint' requires a 'checkpoint_meta' block");
  }
  if (kind === 'policy' && !data.policy_meta) {
    errors.push("kind 'policy' requires a 'policy_meta' block");
  }

  const desc = data.description || '';
  if (desc.length > 200) {
    warnings.push(
      `description is ${desc.length} chars (recommended: ≤ 200). ` +
      `Use 'long_description' for extended text.`
    );
  }

  if (strict) {
    if (!data.canonical_source_url) warnings.push("--strict: no 'canonical_source_url' set");
    if (!data.license) warnings.push("--strict: no 'license' field (use SPDX identifier e.g. MIT)");
    if (!data.tags || !data.tags.length) warnings.push("--strict: no 'tags' — improves discoverability");
    if (!data.frameworks || !data.frameworks.length) warnings.push("--strict: no 'frameworks' — specify target agent frameworks");
  }

  return { errors, warnings };
}

/**
 * Validate a capability.yaml file.
 *
 * @param {string} filePath - Path to capability.yaml
 * @param {object} options
 * @param {boolean} options.strict - Check recommended fields
 * @param {boolean} options.useRemoteSchema - Fetch JSON Schema for validation
 * @returns {Promise<{valid: boolean, errors: string[], warnings: string[], name: string, kind: string, version: string}>}
 */
async function validate(filePath, { strict = false, useRemoteSchema = true } = {}) {
  const result = { valid: false, errors: [], warnings: [], name: '', kind: '', version: '' };

  if (!fs.existsSync(filePath)) {
    result.errors.push(`File not found: ${filePath}`);
    return result;
  }

  if (!yaml) {
    result.errors.push("js-yaml not installed — run: npm install js-yaml");
    return result;
  }

  let data;
  try {
    const text = fs.readFileSync(filePath, 'utf8');
    data = yaml.load(text);
  } catch (e) {
    result.errors.push(`YAML parse error: ${e.message}`);
    return result;
  }

  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    result.errors.push('capability.yaml must be a YAML mapping (object), not a list or scalar');
    return result;
  }

  // Required fields
  for (const field of ['name', 'version', 'kind', 'description']) {
    if (!data[field]) {
      result.errors.push(`Required field missing or empty: '${field}'`);
    }
  }

  // JSON Schema validation
  if (useRemoteSchema && Ajv && result.errors.length === 0) {
    const schema = await fetchSchema();
    if (schema) {
      try {
        const ajv = new Ajv({ strict: false, allErrors: true });
        const validate_fn = ajv.compile(schema);
        if (!validate_fn(data)) {
          for (const err of (validate_fn.errors || [])) {
            result.errors.push(`Schema: ${err.message} (at ${err.instancePath || 'root'})`);
          }
        }
      } catch {}
    }
  }

  // Semantic checks
  const { errors: semErrors, warnings: semWarnings } = semanticChecks(data, strict);
  result.errors.push(...semErrors);
  result.warnings.push(...semWarnings);

  result.valid = result.errors.length === 0;
  result.name = data.name || '';
  result.kind = data.kind || '';
  result.version = data.version || '';

  return result;
}

function printHuman(result, filePath) {
  if (result.valid) {
    console.log(`✅  ${filePath} is valid (capability.yaml v1.0)`);
    if (result.name)    console.log(`    Name:    ${result.name}`);
    if (result.kind)    console.log(`    Kind:    ${result.kind}`);
    if (result.version) console.log(`    Version: ${result.version}`);
  } else {
    console.log(`❌  ${filePath} is INVALID`);
    for (const err of result.errors) {
      console.log(`    ERROR: ${err}`);
    }
  }
  if (result.warnings.length) {
    console.log(`    Warnings (${result.warnings.length}):`);
    for (const w of result.warnings) {
      console.log(`      ⚠️  ${w}`);
    }
  } else if (result.valid) {
    console.log(`    Issues:  None`);
  }
}

// CLI entry point
if (require.main === module) {
  const args = process.argv.slice(2);
  const filePath = args.find(a => !a.startsWith('--')) || 'capability.yaml';
  const strict = args.includes('--strict');
  const jsonOutput = args.includes('--json');
  const noSchema = args.includes('--no-schema');

  validate(filePath, { strict, useRemoteSchema: !noSchema }).then((result) => {
    if (jsonOutput) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      printHuman(result, filePath);
    }
    process.exit(result.valid ? 0 : 1);
  });
}

module.exports = { validate };

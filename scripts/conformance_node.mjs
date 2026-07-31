#!/usr/bin/env node

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

function canonicalize(value) {
  if (value === null || typeof value === "boolean" || typeof value === "string") {
    return JSON.stringify(value);
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new TypeError("RFC 8785 does not permit non-finite numbers");
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map(canonicalize).join(",")}]`;
  }
  if (typeof value === "object") {
    return `{${Object.keys(value)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonicalize(value[key])}`)
      .join(",")}}`;
  }
  throw new TypeError(`unsupported JSON value: ${typeof value}`);
}

function matchesType(value, expected) {
  const types = Array.isArray(expected) ? expected : [expected];
  return types.some((type) => {
    if (type === "null") return value === null;
    if (type === "array") return Array.isArray(value);
    if (type === "object") return value !== null && typeof value === "object" && !Array.isArray(value);
    if (type === "integer") return Number.isInteger(value);
    return typeof value === type;
  });
}

function validate(schema, instance, path = "$") {
  const errors = [];
  if (schema.type !== undefined && !matchesType(instance, schema.type)) {
    return [`${path}: type mismatch`];
  }
  if (schema.const !== undefined && JSON.stringify(instance) !== JSON.stringify(schema.const)) {
    errors.push(`${path}: const mismatch`);
  }
  if (schema.enum !== undefined && !schema.enum.some((item) => JSON.stringify(item) === JSON.stringify(instance))) {
    errors.push(`${path}: enum mismatch`);
  }
  if (typeof instance === "number" && schema.minimum !== undefined && instance < schema.minimum) {
    errors.push(`${path}: below minimum`);
  }
  if (instance !== null && typeof instance === "object" && !Array.isArray(instance)) {
    for (const key of schema.required ?? []) {
      if (!Object.hasOwn(instance, key)) errors.push(`${path}: missing ${key}`);
    }
    if (schema.additionalProperties === false) {
      for (const key of Object.keys(instance)) {
        if (!Object.hasOwn(schema.properties ?? {}, key)) {
          errors.push(`${path}: unexpected ${key}`);
        }
      }
    }
    for (const [key, childSchema] of Object.entries(schema.properties ?? {})) {
      if (Object.hasOwn(instance, key)) {
        errors.push(...validate(childSchema, instance[key], `${path}.${key}`));
      }
    }
  }
  return errors;
}

const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(scriptDirectory, "..");
const corpusPath = process.argv[2]
  ? resolve(process.cwd(), process.argv[2])
  : resolve(repositoryRoot, "conformance/v1/corpus.json");
const corpus = JSON.parse(readFileSync(corpusPath, "utf8"));
const results = [];
let failed = false;

for (const testCase of corpus.cases) {
  const canonical = canonicalize(testCase.instance);
  const digest = createHash("sha256").update(canonical).digest("hex");
  const hashMatches = digest === testCase.expected_sha256;
  let schemaValid = null;
  let schemaErrors = [];
  if (testCase.schema !== null) {
    const schemaPath = resolve(dirname(corpusPath), testCase.schema);
    const schema = JSON.parse(readFileSync(schemaPath, "utf8"));
    schemaErrors = validate(schema, testCase.instance);
    schemaValid = schemaErrors.length === 0;
  }
  const passed =
    hashMatches &&
    (testCase.expected_valid === null || schemaValid === testCase.expected_valid);
  failed ||= !passed;
  results.push({
    case_id: testCase.case_id,
    passed,
    sha256: digest,
    hash_matches: hashMatches,
    schema_valid: schemaValid,
    schema_errors: schemaErrors,
  });
}

process.stdout.write(
  `${JSON.stringify(
    {
      runner: "node-standard-library",
      runtime: process.version,
      corpus_version: corpus.corpus_version,
      results,
    },
    null,
    2,
  )}\n`,
);
process.exitCode = failed ? 1 : 0;

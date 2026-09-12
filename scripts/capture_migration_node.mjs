#!/usr/bin/env node
// Experimental structured-object conformance runner, not a JSONL storage adapter.
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";

function canonical(value) {
  if (typeof value === "string") {
    if (!value.isWellFormed()) throw new Error("invalid Unicode");
    return JSON.stringify(value);
  }
  if (value === null || typeof value === "boolean") return JSON.stringify(value);
  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new Error("unsupported JSON number");
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (object(value)) return `{${Object.keys(value).sort().map(key => `${canonical(key)}:${canonical(value[key])}`).join(",")}}`;
  throw new Error("unsupported JSON value");
}
const object = value => value !== null && typeof value === "object" && !Array.isArray(value);
const exact = (value, keys) => object(value) && Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const hash = value => createHash("sha256").update(canonical(value)).digest("hex");
// Python str.strip also treats U+001C..U+001F and U+0085 as whitespace; JS trim
// additionally strips U+FEFF. Match the source contract explicitly.
const nonblank = value => typeof value === "string" && /[^\u0009-\u000d\u001c-\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000]/u.test(value);

function sourceValid(source) {
  if (!exact(source, ["capture_id", "record", "record_sha256"])) throw new Error("source fields");
  const record = source.record;
  if (!object(record) || record.schema_version !== "1.0.0" || record.record_type !== "archived_http_capture" || !nonblank(record.source_id)) throw new Error("source contract");
  const digest = hash(record);
  if (source.record_sha256 !== digest || source.capture_id !== `urn:riopa:capture:sha256:${digest}`) throw new Error("source integrity");
}
function facetsValid(facets) {
  if (!object(facets) || Object.keys(facets).some(key => !["quality", "source_rights"].includes(key))) throw new Error("facet fields");
  for (const refs of Object.values(facets)) {
    if (!Array.isArray(refs) || !refs.length) throw new Error("facet references");
    for (const ref of refs) {
      if (!exact(ref, ["uri", "sha256"]) || !nonblank(ref.uri) || typeof ref.sha256 !== "string" || !/^[0-9a-f]{64}$/u.test(ref.sha256) || ref.sha256.length !== 64) throw new Error("facet reference");
    }
  }
}
function migrate(source, facets = {}) {
  sourceValid(source);
  facetsValid(facets);
  const view = {schema_version: "1.1.0", record_type: "archived_capture_view", source, facets};
  return {...view, view_sha256: hash(view)};
}
function recover(view) {
  if (!exact(view, ["schema_version", "record_type", "source", "facets", "view_sha256"]) || view.schema_version !== "1.1.0" || view.record_type !== "archived_capture_view") throw new Error("view contract");
  sourceValid(view.source);
  facetsValid(view.facets);
  const {view_sha256, ...unsigned} = view;
  if (view_sha256 !== hash(unsigned)) throw new Error("view integrity");
  return view.source;
}
const requests = JSON.parse(readFileSync(0, "utf8"));
const results = requests.map(request => {
  try {
    if (request.operation === "migrate") return {accepted: true, value: migrate(request.value, request.facets ?? {})};
    if (request.operation === "recover") return {accepted: true, value: recover(request.value)};
    throw new Error("unsupported operation");
  } catch {
    return {accepted: false};
  }
});
process.stdout.write(JSON.stringify(results) + "\n");

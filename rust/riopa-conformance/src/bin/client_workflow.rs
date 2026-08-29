use std::collections::{BTreeSet, VecDeque};
use std::env;
use std::fs;

use riopa_conformance::canonical_json_sha256;
use serde_json::{Value, json};

fn text<'a>(value: &'a Value, key: &str) -> Result<&'a str, String> {
    value
        .get(key)
        .and_then(Value::as_str)
        .filter(|item| !item.is_empty())
        .ok_or_else(|| format!("missing or empty {key}"))
}

fn execute(document: &Value) -> Result<Value, String> {
    if text(document, "contract_version")? != "1.0.0" {
        return Err("unsupported workflow contract_version".into());
    }
    let capture = document.get("capture").ok_or("missing capture")?;
    let capture_id = text(capture, "capture_id")?;
    let payload = capture.get("payload").ok_or("missing capture payload")?;
    let actual_digest = canonical_json_sha256(payload).map_err(|_| "invalid capture payload")?;
    if actual_digest != text(capture, "expected_sha256")? {
        return Err("capture payload digest mismatch".into());
    }

    let required = document
        .pointer("/validation/required_fields")
        .and_then(Value::as_array)
        .ok_or("missing validation required_fields")?;
    for field in required {
        let field = field
            .as_str()
            .ok_or("required field names must be strings")?;
        text(payload, field)?;
    }

    let query = document
        .get("lineage_query")
        .ok_or("missing lineage_query")?;
    let query_fields: BTreeSet<&str> = query
        .as_object()
        .ok_or("lineage_query must be an object")?
        .keys()
        .map(String::as_str)
        .collect();
    let expected_query_fields =
        BTreeSet::from(["contract_version", "node_id", "question", "max_depth"]);
    if query_fields != expected_query_fields {
        return Err("lineage query fields must match the 1.0.0 contract".into());
    }
    if text(query, "contract_version")? != "1.0.0" || text(query, "question")? != "why" {
        return Err("unsupported lineage query".into());
    }
    let node_id = text(query, "node_id")?;
    let max_depth = query
        .get("max_depth")
        .and_then(Value::as_u64)
        .filter(|depth| (1..=100).contains(depth))
        .ok_or("max_depth must be between 1 and 100")?;
    let edges = document
        .get("lineage_edges")
        .and_then(Value::as_array)
        .ok_or("missing lineage_edges")?;
    let mut queue = VecDeque::from([(node_id.to_owned(), 0_u64)]);
    let mut found = BTreeSet::new();
    while let Some((target, depth)) = queue.pop_front() {
        if depth >= max_depth {
            continue;
        }
        for edge in edges {
            if text(edge, "target")? == target {
                let source = text(edge, "source")?.to_owned();
                if found.insert(source.clone()) {
                    queue.push_back((source, depth + 1));
                }
            }
        }
    }
    let lineage: Vec<String> = found.into_iter().collect();
    let mut expected: Vec<String> = document
        .get("expected_lineage")
        .and_then(Value::as_array)
        .ok_or("missing expected_lineage")?
        .iter()
        .map(|item| {
            item.as_str()
                .map(str::to_owned)
                .ok_or("lineage IDs must be strings")
        })
        .collect::<Result<_, _>>()?;
    expected.sort();
    if lineage != expected {
        return Err("lineage query result mismatch".into());
    }
    Ok(json!({
        "contract_version": "1.0.0",
        "capture_id": capture_id,
        "capture_sha256": actual_digest,
        "capture_status": "passed",
        "validation_status": "passed",
        "lineage_status": "passed",
        "lineage": lineage
    }))
}

fn main() {
    let path = env::args().nth(1).unwrap_or_default();
    if path.is_empty() {
        eprintln!("usage: client_workflow <fixture.json>");
        std::process::exit(2);
    }
    let result = fs::read_to_string(path)
        .map_err(|error| error.to_string())
        .and_then(|text| serde_json::from_str(&text).map_err(|error| error.to_string()))
        .and_then(|document| execute(&document));
    match result {
        Ok(report) => println!("{}", serde_json::to_string(&report).unwrap()),
        Err(error) => {
            eprintln!("client workflow failed: {error}");
            std::process::exit(1);
        }
    }
}

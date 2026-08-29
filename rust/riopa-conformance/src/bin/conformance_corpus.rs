use std::fs;
use std::path::PathBuf;

use riopa_conformance::canonical_json_sha256;

fn main() {
    let repository_root = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("../..")
        .canonicalize()
        .expect("repository root must resolve");
    let corpus_path = repository_root.join("conformance/v1/corpus.json");
    let text = fs::read_to_string(&corpus_path).expect("conformance corpus must be readable");
    let corpus: serde_json::Value =
        serde_json::from_str(&text).expect("conformance corpus must be valid JSON");
    let cases = corpus
        .get("cases")
        .and_then(serde_json::Value::as_array)
        .expect("conformance corpus cases must be an array");
    for case in cases {
        let case_id = case
            .get("case_id")
            .and_then(serde_json::Value::as_str)
            .expect("conformance case_id must be a string");
        let instance = case
            .get("instance")
            .expect("conformance case instance is required");
        let digest = canonical_json_sha256(instance).expect("corpus value must be supported");
        let expected_digest = case
            .get("expected_sha256")
            .and_then(serde_json::Value::as_str)
            .expect("expected_sha256 must be a string");
        let hash_matches = digest == expected_digest;
        let (schema_valid, schema_matches) = match case.get("schema") {
            None | Some(serde_json::Value::Null) => (None, true),
            Some(serde_json::Value::String(relative)) => {
                let schema_path = corpus_path
                    .parent()
                    .expect("corpus parent")
                    .join(relative)
                    .canonicalize()
                    .expect("schema path must resolve");
                assert!(
                    schema_path.starts_with(&repository_root),
                    "schema path must remain inside repository"
                );
                let schema_text = fs::read_to_string(schema_path).expect("schema must be readable");
                let schema: serde_json::Value =
                    serde_json::from_str(&schema_text).expect("schema must be valid JSON");
                let validator = jsonschema::draft202012::options()
                    .should_validate_formats(true)
                    .build(&schema)
                    .expect("schema must compile as Draft 2020-12");
                let actual = validator.is_valid(instance);
                let expected = case
                    .get("expected_valid")
                    .and_then(serde_json::Value::as_bool)
                    .expect("expected_valid must be boolean when schema is present");
                (Some(actual), actual == expected)
            }
            _ => panic!("schema must be a relative string or null"),
        };
        println!(
            "{}",
            serde_json::json!({
                "case_id": case_id,
                "sha256": digest,
                "hash_matches": hash_matches,
                "schema_valid": schema_valid,
                "schema_matches": schema_matches,
                "passed": hash_matches && schema_matches,
            })
        );
        assert!(
            hash_matches && schema_matches,
            "conformance case {case_id} failed"
        );
    }
}

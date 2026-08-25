use std::fs;
use std::path::PathBuf;

use riopa_conformance::canonical_json_sha256;

fn main() {
    let corpus_path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../conformance/v1/corpus.json");
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
        println!("{case_id}\t{digest}");
    }
}

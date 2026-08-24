use std::env;
use std::io::{self, Read};

use riopa_conformance::{Confidence, Crosswalk};

fn fixture() -> Crosswalk {
    Crosswalk {
        mapping_id: "urn:riopa:mapping:exchange".into(),
        source_id: "source:fixture".into(),
        canonical_id: "urn:riopa:concept:example".into(),
        confidence: Confidence::Medium,
        evidence: vec!["fixture:exchange".into()],
    }
}

fn main() {
    let mode = env::args().nth(1).unwrap_or_default();
    let result = match mode.as_str() {
        "produce" => fixture().to_wire(),
        "consume" => {
            let mut input = String::new();
            io::stdin().read_to_string(&mut input).unwrap();
            Crosswalk::from_wire(input.trim_end()).map(|value| value.to_wire().unwrap())
        }
        _ => {
            eprintln!("usage: conformance_exchange <produce|consume>");
            std::process::exit(2);
        }
    };
    match result {
        Ok(value) => println!("{value}"),
        Err(error) => {
            eprintln!("invalid conformance exchange: {error:?}");
            std::process::exit(1);
        }
    }
}

//! Bounded Rust models for the RIOPA conformance contract.
//!
//! This crate validates typed values and the bounded canonical-hash corpus
//! runner. It does not claim standards-complete serialization or independent
//! external conformance.

use sha2::{Digest, Sha256};

/// Canonicalise an I-JSON value using RFC 8785 / JCS semantics.
pub fn canonical_json(value: &serde_json::Value) -> Result<String, ValidationError> {
    serde_json_canonicalizer::to_string(value).map_err(|_| ValidationError::InvalidWireField)
}

/// Return a SHA-256 digest over the bounded canonical JSON representation.
pub fn canonical_json_sha256(value: &serde_json::Value) -> Result<String, ValidationError> {
    let canonical = canonical_json(value)?;
    let digest = Sha256::digest(canonical.as_bytes());
    Ok(format!("{digest:x}"))
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Crosswalk {
    pub mapping_id: String,
    pub source_id: String,
    pub canonical_id: String,
    pub confidence: Confidence,
    pub evidence: Vec<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Confidence {
    High,
    Medium,
    Low,
    Unknown,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ValidationError {
    EmptyField(&'static str),
    UnknownConfidence,
    EvidenceRequired,
    InvalidWireField,
}

impl Crosswalk {
    /// Encode the bounded exchange fixture as a deterministic tab-separated record.
    ///
    /// This intentionally supports the exercise's restricted fixture alphabet only;
    /// it is not a general interchange format or a release serialization.
    pub fn to_wire(&self) -> Result<String, ValidationError> {
        self.validate().map_err(|errors| errors[0].clone())?;
        if [&self.mapping_id, &self.source_id, &self.canonical_id]
            .iter()
            .any(|value| value.contains(['\t', '\n', '\r']))
            || self
                .evidence
                .iter()
                .any(|value| value.contains(['\t', '\n', '\r', ',']))
        {
            return Err(ValidationError::InvalidWireField);
        }
        let confidence = match self.confidence {
            Confidence::High => "high",
            Confidence::Medium => "medium",
            Confidence::Low => "low",
            Confidence::Unknown => "unknown",
        };
        Ok(format!(
            "{}\t{}\t{}\t{}\t{}",
            self.mapping_id,
            self.source_id,
            self.canonical_id,
            confidence,
            self.evidence.join(",")
        ))
    }

    /// Decode the restricted exchange fixture emitted by `to_wire`.
    pub fn from_wire(value: &str) -> Result<Self, ValidationError> {
        let fields: Vec<&str> = value.split('\t').collect();
        if fields.len() != 5 || fields.iter().any(|field| field.is_empty()) {
            return Err(ValidationError::InvalidWireField);
        }
        let confidence = match fields[3] {
            "high" => Confidence::High,
            "medium" => Confidence::Medium,
            "low" => Confidence::Low,
            "unknown" => Confidence::Unknown,
            _ => return Err(ValidationError::InvalidWireField),
        };
        let evidence = if fields[4].is_empty() {
            Vec::new()
        } else {
            fields[4].split(',').map(str::to_owned).collect()
        };
        let result = Self {
            mapping_id: fields[0].to_owned(),
            source_id: fields[1].to_owned(),
            canonical_id: fields[2].to_owned(),
            confidence,
            evidence,
        };
        result.validate().map_err(|errors| errors[0].clone())?;
        Ok(result)
    }

    pub fn validate(&self) -> Result<(), Vec<ValidationError>> {
        let mut errors = Vec::new();
        if self.mapping_id.is_empty() {
            errors.push(ValidationError::EmptyField("mapping_id"));
        }
        if self.source_id.is_empty() {
            errors.push(ValidationError::EmptyField("source_id"));
        }
        if self.canonical_id.is_empty() {
            errors.push(ValidationError::EmptyField("canonical_id"));
        }
        if self.confidence == Confidence::Unknown && self.evidence.is_empty() {
            errors.push(ValidationError::EvidenceRequired);
        }
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MigrationCase {
    pub profile: String,
    pub target_profile: String,
    pub migration: String,
}

impl MigrationCase {
    pub fn validate(&self) -> Result<(), Vec<ValidationError>> {
        let mut errors = Vec::new();
        if self.profile.is_empty() {
            errors.push(ValidationError::EmptyField("profile"));
        }
        if self.target_profile.is_empty() {
            errors.push(ValidationError::EmptyField("target_profile"));
        }
        if self.migration.is_empty() {
            errors.push(ValidationError::EmptyField("migration"));
        }
        if errors.is_empty() {
            Ok(())
        } else {
            Err(errors)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_crosswalk() -> Crosswalk {
        Crosswalk {
            mapping_id: "urn:riopa:mapping:rust".into(),
            source_id: "source-1".into(),
            canonical_id: "urn:riopa:concept:example".into(),
            confidence: Confidence::Medium,
            evidence: vec!["fixture:rust".into()],
        }
    }

    #[test]
    fn valid_crosswalk_passes() {
        assert_eq!(valid_crosswalk().validate(), Ok(()));
    }

    #[test]
    fn uncertain_crosswalk_requires_evidence() {
        let mut value = valid_crosswalk();
        value.confidence = Confidence::Unknown;
        value.evidence.clear();
        assert_eq!(
            value.validate(),
            Err(vec![ValidationError::EvidenceRequired])
        );
    }

    #[test]
    fn migration_requires_all_fields() {
        let value = MigrationCase {
            profile: "v1".into(),
            target_profile: "v1.1".into(),
            migration: "additive-field-preserved".into(),
        };
        assert_eq!(value.validate(), Ok(()));
    }

    #[test]
    fn wire_exchange_round_trips() {
        let value = valid_crosswalk();
        let encoded = value.to_wire().expect("fixture should encode");
        assert_eq!(Crosswalk::from_wire(&encoded), Ok(value));
    }

    #[test]
    fn wire_exchange_rejects_ambiguous_fields() {
        let mut value = valid_crosswalk();
        value.mapping_id.push('\t');
        assert_eq!(value.to_wire(), Err(ValidationError::InvalidWireField));
    }

    #[test]
    fn canonical_json_supports_rfc8785_numbers_and_utf16_key_order() {
        let value: serde_json::Value = serde_json::from_str(
            r#"{"\u20ac":"euro","\r":"control","1":1e-7,"2":1e+21,"3":-0.0,"\ud83d\ude00":"face","\ufb33":"hebrew"}"#,
        )
        .expect("valid I-JSON fixture");
        assert_eq!(
            canonical_json(&value).expect("canonical fixture"),
            r#"{"\r":"control","1":1e-7,"2":1e+21,"3":0,"€":"euro","😀":"face","דּ":"hebrew"}"#
        );
    }
}

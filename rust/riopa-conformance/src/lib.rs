//! Bounded Rust models for the RIOPA conformance contract.
//!
//! This crate validates typed values only. It deliberately does not parse the
//! repository JSON corpus or claim cross-language parity until a separate
//! corpus runner and producer/consumer exercise exist.

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
}

impl Crosswalk {
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
}

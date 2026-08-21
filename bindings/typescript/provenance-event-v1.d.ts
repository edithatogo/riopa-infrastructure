/** Bounded TypeScript consumer model for the RIOPA provenance event v1 schema. */
export type ProvenanceAgentType =
  | "person"
  | "organisation"
  | "software"
  | "service"
  | "workflow";

export interface ProvenanceAgent {
  agent_id: string;
  agent_type: ProvenanceAgentType;
  role: string;
  name?: string | null;
  version?: string | null;
  identifier?: string | null;
}

export interface ProvenanceActivity {
  activity_id: string;
  activity_type: string;
  name?: string | null;
  description?: string | null;
  [key: string]: unknown;
}

export interface ProvenanceEventV1 {
  schema_version: "1.0.0";
  event_id: string;
  stream_id: string;
  sequence: number;
  event_type: string;
  status: string;
  occurred_at: string;
  recorded_at: string;
  activity: ProvenanceActivity;
  agents: ProvenanceAgent[];
  inputs: string[];
  outputs: string[];
  event_hash: string;
  parameters?: Record<string, unknown>;
  environment?: Record<string, unknown>;
  schema_refs?: string[];
  classification_refs?: string[];
  causal_parents?: string[];
  [key: string]: unknown;
}

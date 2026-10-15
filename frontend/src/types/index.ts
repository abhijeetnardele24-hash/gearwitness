export type CaptureView = "front" | "back" | "top" | "accessories" | "detail";

export type ProposalDecision = "pending" | "confirmed" | "dismissed" | "uncertain";

export type ConditionType =
  | "scratch"
  | "scuff"
  | "dent"
  | "crack"
  | "missing_accessory"
  | "normal_wear"
  | "artifact_lighting"
  | "unknown";

export type Severity = "none" | "minor" | "moderate" | "severe";

export interface KitItem {
  id: string;
  name: string;
  quantity: number;
  description?: string;
  is_present_checkout: boolean;
  is_present_checkin?: boolean | null;
  serial_or_part_no?: string;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface ChangeProposal {
  id: string;
  inspection_id: string;
  capture_view: CaptureView;
  bounding_box: BoundingBox;
  checkout_crop_path?: string;
  checkin_crop_path?: string;
  checkout_crop_url?: string;
  checkin_crop_url?: string;
  condition_type: ConditionType;
  severity: Severity;
  confidence: number;
  description: string;
  model_rationale: string;
  operator_decision: ProposalDecision;
  operator_notes?: string;
  resolved_at?: string;
}

export interface MediaEvidence {
  id: string;
  filename: string;
  storage_path: string;
  public_url?: string;
  sha256_hash: string;
  file_size_bytes: number;
  mime_type: string;
  width: number;
  height: number;
  capture_view: CaptureView;
  captured_at: string;
  is_checkout: boolean;
}

export interface Inspection {
  id: string;
  asset_id: string;
  asset_name: string;
  serial_number: string;
  customer_reference: string;
  status: "created" | "checkout_captured" | "checkin_captured" | "analyzing" | "review_ready" | "approved";
  checkout_timestamp?: string;
  checkin_timestamp?: string;
  media: MediaEvidence[];
  proposals: ChangeProposal[];
  kit_checklist: KitItem[];
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface HealthResponse {
  status: string;
  app_mode: "fixture" | "local";
  version: string;
  ollama_connected: boolean;
  model_name: string;
  target_model?: string;
  model_available: boolean;
  timestamp: string;
}

export interface ExportManifest {
  inspection_id: string;
  asset_name: string;
  serial_number: string;
  customer_reference: string;
  checkout_timestamp?: string;
  checkin_timestamp?: string;
  generated_at: string;
  gearwitness_version: string;
  app_mode: string;
  model_used?: string;
  source_media_hashes: Record<string, string>;
  total_proposals: number;
  confirmed_proposals: number;
  dismissed_proposals: number;
  uncertain_proposals: number;
  checklist_status: Record<string, boolean>;
  disclaimer: string;
  manifest_hash_sha256?: string;
}

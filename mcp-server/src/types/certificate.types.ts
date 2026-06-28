import { ExplainableResult } from './regulatory.types';

export interface AuditCertificate extends ExplainableResult {
  vc_json: any;
  pdf_base64: string;
  issued_at: string;
}

export interface DriftAlert extends ExplainableResult {
  drift_detected: boolean;
  drift_metrics: Record<string, number>;
  threshold_exceeded: string[];
  reaudit_recommended: boolean;
}

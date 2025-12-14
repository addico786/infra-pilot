export type FileType = "terraform" | "kubernetes";

export type TimelineSeverity = "info" | "low" | "medium" | "high";

export type IssueSeverity = "low" | "medium" | "high" | "critical";

export interface AnalyzeRequest {
  content: string;
  file_type: FileType;
  model?: string;
}

export interface TimelineEvent {
  day: number;
  event: string;
  severity: TimelineSeverity;
}

export interface Issue {
  id: string;
  title: string;
  description: string;
  severity: IssueSeverity;
  resource: string;
  fix_suggestion: string;
  // AI-enhanced fields (may be present in response)
  explanation?: string;
  future_impact?: string;
  // Oumi RL scoring (optional)
  oumi_score?: number;
}

export interface AnalyzeResponse {
  drift_score: number;
  timeline: TimelineEvent[];
  issues: Issue[];
  provider?: string;
  model?: string;
}

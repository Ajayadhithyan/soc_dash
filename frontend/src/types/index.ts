export interface AlertEvent {
  id: string;
  timestamp: string;
  src_ip: string;
  dest_ip: string;
  event_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  user: string;
  raw_log: string;
  ai_summary?: string;
  risk_score?: number;
  risk_label?: string;
  anomaly_score?: number;
  cvss_base?: number;
  asset_criticality?: number;
  asset_type?: string;
  mitre?: MitreMapping;
  threat_intel?: ThreatIntel;
  sigma_matches?: SigmaMatch[];
  correlation?: CorrelationResult;
  feedback?: FeedbackResult;
  playbook?: Playbook;
  auto_response?: Record<string, unknown>;
  auto_playbook_actions?: AutoPlaybookAction[];
  analyst_verification?: 'TRUE_POSITIVE' | 'FALSE_POSITIVE';
  isNew?: boolean;
}

export interface MitreMapping {
  technique_id: string;
  technique_name: string;
  tactic: string;
  description: string;
  sub_techniques: string[];
  severity_boost: number;
  llm_analysis?: string;
}

export interface ThreatIntel {
  is_known_malicious: boolean;
  blocklist_source?: string;
  threat_category?: string;
  risk_multiplier: number;
  analyst_blocked: boolean;
}

export interface SigmaMatch {
  rule_id: string;
  rule_name: string;
  severity: string;
  description: string;
  tags: string[];
}

export interface CorrelationResult {
  is_correlated: boolean;
  campaign_id: string | null;
  primary_pattern: string | null;
  total_risk_boost: number;
  related_alert_count: number;
  patterns: CorrelationPattern[];
}

export interface CorrelationPattern {
  pattern_name: string;
  risk_boost: number;
  campaign_id?: string;
  matched_events_count?: number;
  unique_targets?: number;
  target_ips?: string[];
  unique_attack_types?: number;
  attack_types?: string[];
}

export interface FeedbackResult {
  feedback_confidence: number;
  suppress_recommendation: boolean;
  classifier_trained: boolean;
}

export interface Playbook {
  name: string;
  steps: string[];
  severity: string;
  estimated_time: string;
}

export interface AutoPlaybookAction {
  playbook_rule: string;
  action: string;
  triggered_at: string;
  auto_triggered: boolean;
}

export interface StatsOverview {
  total_alerts: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  avg_risk_score: number;
  active_threats: number;
  alerts_last_hour: number;
}

export interface GeoData {
  country: string;
  count: number;
  lat: number;
  lng: number;
}

export interface TopSource {
  ip: string;
  count: number;
  last_seen: string;
  primary_attack: string;
}

export interface ChatMessage {
  sender: 'user' | 'bot';
  text: string;
  context_alerts_used?: number;
}

export interface AuditLog {
  timestamp: string;
  alert_id: string;
  action: string;
  analyst_user: string;
  success: boolean;
  details: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  alerts: T[];
  total: number;
  page: number;
  per_page: number;
}

export interface SystemHealth {
  status: string;
  service: string;
  database: string;
  gemini_api: string;
  anomaly_detector: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message?: string;
  duration?: number;
}

export interface AlertFilters {
  search: string;
  severity: string;
  eventType: string;
  page?: number;
}

export interface EventTypeDistribution {
  event_type: string;
  count: number;
}

export interface RiskDistribution {
  label: string;
  count: number;
}

export interface User {
  username: string;
  role: string;
}

export type SortField = 'timestamp' | 'severity' | 'event_type' | 'src_ip' | 'dest_ip' | 'risk_score';
export type SortOrder = 'asc' | 'desc';

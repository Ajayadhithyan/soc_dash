import axios from 'axios';
import type {
  StatsOverview,
  GeoData,
  TopSource,
  AlertEvent,
  AuditLog,
  PaginatedResponse,
  SystemHealth,
  EventTypeDistribution,
  RiskDistribution,
} from '../types';

export interface TimelineData {
  timeline: { time: string; count: number }[];
  range: string;
}

export interface SeverityData {
  distribution: { severity: string; count: number }[];
}

export interface ChatResponse {
  response: string;
  context_alerts_used: number;
}

export interface TrainResponse {
  success: boolean;
  message: string;
  anomaly_detector: string;
}

export interface VerifyResponse {
  success: boolean;
  message: string;
}

const api = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const login = async (username: string, password: string): Promise<{ access_token: string }> => {
  const response = await api.post('/api/auth/login', { username, password });
  return response.data;
};

export const getOverview = async (): Promise<StatsOverview> => {
  const response = await api.get('/api/stats/overview');
  return response.data;
};

export const getSeverityDistribution = async (): Promise<SeverityData> => {
  const response = await api.get('/api/stats/severity');
  return response.data;
};

export const getEventTypes = async (): Promise<{ event_types: EventTypeDistribution[] }> => {
  const response = await api.get('/api/stats/event-types');
  return response.data;
};

export const getTimeline = async (range = '6h'): Promise<TimelineData> => {
  const response = await api.get('/api/stats/timeline', { params: { range } });
  return response.data;
};

export const getTopSources = async (): Promise<{ sources: TopSource[] }> => {
  const response = await api.get('/api/stats/top-sources');
  return response.data;
};

export const getGeoData = async (): Promise<{ geo_threats: GeoData[] }> => {
  const response = await api.get('/api/stats/geo');
  return response.data;
};

export const getRiskDistribution = async (): Promise<{ risk_distribution: RiskDistribution[] }> => {
  const response = await api.get('/api/stats/risk-distribution');
  return response.data;
};

export const getAlerts = async (params: Record<string, unknown> = {}): Promise<PaginatedResponse<AlertEvent>> => {
  const response = await api.get('/api/alerts', { params });
  return response.data;
};

export const getAlertDetail = async (alertId: string): Promise<AlertEvent> => {
  const response = await api.get(`/api/alerts/${alertId}`);
  return response.data;
};

export const respondToAlert = async (alertId: string, action: string): Promise<Record<string, unknown>> => {
  const response = await api.post(`/api/alerts/${alertId}/respond`, null, {
    params: { action },
  });
  return response.data;
};

export const sendChatMessage = async (message: string): Promise<ChatResponse> => {
  const response = await api.post('/api/chat', { message });
  return response.data;
};

export const trainModel = async (): Promise<TrainResponse> => {
  const response = await api.post('/api/model/train');
  return response.data;
};

export const trainFeedbackModel = async (): Promise<Record<string, unknown>> => {
  const response = await api.post('/api/model/train-feedback');
  return response.data;
};

export const verifyAlert = async (alertId: string, status: string): Promise<VerifyResponse> => {
  const response = await api.post(`/api/alerts/${alertId}/verify`, null, {
    params: { status },
  });
  return response.data;
};

export const getAuditLogs = async (limit = 50): Promise<{ audit_logs: AuditLog[]; count: number }> => {
  const response = await api.get('/api/audit', { params: { limit } });
  return response.data;
};

export const checkHealth = async (): Promise<SystemHealth> => {
  const response = await api.get('/api/health');
  return response.data;
};

export function exportAlertsToCsv(alerts: AlertEvent[]) {
  const headers = ['Timestamp', 'Severity', 'Event Type', 'Source IP', 'Destination IP', 'Risk Score', 'User', 'Raw Log'];
  const rows = alerts.map((a) => [
    a.timestamp,
    a.severity,
    a.event_type,
    a.src_ip,
    a.dest_ip,
    String(a.risk_score ?? ''),
    a.user,
    `"${(a.raw_log || '').replace(/"/g, '""')}"`,
  ]);
  const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `soc-alerts-${new Date().toISOString().slice(0, 10)}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

export default api;

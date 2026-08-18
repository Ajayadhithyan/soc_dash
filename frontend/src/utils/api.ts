import axios, { type AxiosRequestConfig } from 'axios';
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
  MitreHeatmapData,
  EndpointInfo,
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
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('soc_token');
      if (window.location.pathname !== '/') {
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// ---- Request caching / dedup ---------------------------------------------
// Stats endpoints are fetched in bursts (WebSocket-triggered refreshes, manual
// refresh, tab switches, StrictMode double-effects). A short TTL + in-flight
// promise dedup collapses concurrent duplicate GETs into a single network call.
interface CacheEntry {
  data: unknown;
  expiresAt: number;
}

const GET_TTL_MS = 1500;
const getCache = new Map<string, CacheEntry>();
const inflight = new Map<string, Promise<unknown>>();

function buildKey(url: string, params?: unknown): string {
  return `${url}${JSON.stringify(params ?? {})}`;
}

export const cachedGet = async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
  const key = buildKey(url, config?.params);

  const pending = inflight.get(key);
  if (pending) return pending as Promise<T>;

  const hit = getCache.get(key);
  if (hit && hit.expiresAt > Date.now()) return hit.data as T;

  const request = api
    .get<T>(url, config)
    .then((response) => {
      getCache.set(key, { data: response.data, expiresAt: Date.now() + GET_TTL_MS });
      inflight.delete(key);
      return response.data;
    })
    .catch((error) => {
      inflight.delete(key);
      throw error;
    });

  inflight.set(key, request);
  return request;
};

export const login = async (username: string, password: string): Promise<{ access_token: string }> => {
  const response = await api.post('/api/auth/login', { username, password });
  return response.data;
};

export const getOverview = async (): Promise<StatsOverview> => {
  return cachedGet<StatsOverview>('/api/stats/overview');
};

export const getSeverityDistribution = async (): Promise<SeverityData> => {
  return cachedGet<SeverityData>('/api/stats/severity');
};

export const getEventTypes = async (): Promise<{ event_types: EventTypeDistribution[] }> => {
  return cachedGet('/api/stats/event-types');
};

export const getTimeline = async (range = '6h'): Promise<TimelineData> => {
  return cachedGet<TimelineData>('/api/stats/timeline', { params: { range } });
};

export const getTopSources = async (): Promise<{ sources: TopSource[] }> => {
  return cachedGet('/api/stats/top-sources');
};

export const getGeoData = async (): Promise<{ geo_threats: GeoData[] }> => {
  return cachedGet('/api/stats/geo');
};

export const getRiskDistribution = async (): Promise<{ risk_distribution: RiskDistribution[] }> => {
  return cachedGet('/api/stats/risk-distribution');
};

export const getMitreHeatmap = async (): Promise<MitreHeatmapData> => {
  return cachedGet<MitreHeatmapData>('/api/stats/mitre');
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
  return cachedGet<SystemHealth>('/api/health');
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

export const getSyntheticConfig = async (): Promise<{ enabled: boolean }> => {
  const response = await api.get('/api/alerts/config/synthetic');
  return response.data;
};

export const toggleSyntheticConfig = async (enabled: boolean): Promise<{ success: boolean; enabled: boolean }> => {
  const response = await api.post('/api/alerts/config/synthetic', null, { params: { enabled } });
  return response.data;
};

export const ingestLogs = async (logs: (string | object)[]): Promise<{ success: boolean; count: number }> => {
  const response = await api.post('/api/alerts/ingest', { logs });
  return response.data;
};

export const getEndpoints = async (): Promise<{ endpoints: EndpointInfo[]; total: number; offline_timeout_seconds: number }> => {
  const response = await api.get('/api/agent/endpoints');
  return response.data;
};

export default api;

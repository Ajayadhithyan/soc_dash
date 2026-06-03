import axios from 'axios';

const api = axios.create({
  baseURL: '', // Proxied via Vite
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getOverview = async () => {
  const response = await api.get('/api/stats/overview');
  return response.data;
};

export const getSeverityDistribution = async () => {
  const response = await api.get('/api/stats/severity');
  return response.data;
};

export const getEventTypes = async () => {
  const response = await api.get('/api/stats/event-types');
  return response.data;
};

export const getTimeline = async () => {
  const response = await api.get('/api/stats/timeline');
  return response.data;
};

export const getTopSources = async () => {
  const response = await api.get('/api/stats/top-sources');
  return response.data;
};

export const getGeoData = async () => {
  const response = await api.get('/api/stats/geo');
  return response.data;
};

export const getAlerts = async (params = {}) => {
  const response = await api.get('/api/alerts', { params });
  return response.data;
};

export const getAlertDetail = async (alertId) => {
  const response = await api.get(`/api/alerts/${alertId}`);
  return response.data;
};

export const respondToAlert = async (alertId, action) => {
  const response = await api.post(`/api/alerts/${alertId}/respond`, null, {
    params: { action },
  });
  return response.data;
};

export const sendChatMessage = async (message) => {
  const response = await api.post('/api/chat', { message });
  return response.data;
};

export const trainModel = async () => {
  const response = await api.post('/api/model/train');
  return response.data;
};

export default api;

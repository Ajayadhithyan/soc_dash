import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'

vi.mock('../utils/api', () => ({
  getOverview: vi.fn().mockResolvedValue({ total_alerts: 0, active_threats: 0, avg_risk_score: 0, critical_count: 0, high_count: 0, medium_count: 0, low_count: 0, alerts_last_hour: 0 }),
  getSeverityDistribution: vi.fn().mockResolvedValue({ distribution: [] }),
  getTimeline: vi.fn().mockResolvedValue({ timeline: [] }),
  getTopSources: vi.fn().mockResolvedValue({ sources: [] }),
  getGeoData: vi.fn().mockResolvedValue({ geo_threats: [] }),
  getAlerts: vi.fn().mockResolvedValue({ alerts: [], total: 0 }),
  getAlertDetail: vi.fn().mockResolvedValue(null),
  respondToAlert: vi.fn(),
  sendChatMessage: vi.fn().mockResolvedValue({ response: '', context_alerts_used: 0 }),
  trainModel: vi.fn().mockResolvedValue({ success: true }),
  verifyAlert: vi.fn().mockResolvedValue({ success: true }),
  checkHealth: vi.fn().mockResolvedValue({ status: 'online', service: '', database: '', gemini_api: '', anomaly_detector: '' }),
}))

describe('App', () => {
  it('renders the dashboard header', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )

    expect(screen.getAllByText(/zenith/i).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(/SOC Platform/i)).toBeTruthy()
  })

  it('renders tab navigation', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    )

    expect(screen.getByText('Incident Triage')).toBeTruthy()
    expect(screen.getByText('Analytics & Trends')).toBeTruthy()
    expect(screen.getByText('AI Copilot Lab')).toBeTruthy()
    expect(screen.getByText('SOAR Audit Trail')).toBeTruthy()
  })
})

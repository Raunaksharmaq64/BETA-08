/**
 * RightFit Dashboard API Endpoints
 * Point these to your premade backend service when ready for live integration.
 * Toggle NEXT_PUBLIC_USE_MOCK_DATA=false in .env.local to activate live backend calls.
 */
export const API_ENDPOINTS = {
  DASHBOARD_DATA: '/api/v1/dashboard',
  DASHBOARD_METRICS: '/api/v1/dashboard/metrics',
  ACTIVE_WORKFLOWS: '/api/v1/workflows/active',
  RUN_WORKFLOW: '/api/v1/workflows/run',
  ACTIVITY_STATS: '/api/v1/dashboard/activity',
  HIGH_VALUE_SIGNALS: '/api/v1/signals/recommendations',
  USER_PROFILE: '/api/v1/user/profile',
  SEARCH: '/api/v1/dashboard/search',
} as const;

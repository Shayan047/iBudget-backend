export const BASE_URL = 'http://localhost:8000';

// Thresholds you'll reuse across all test files
export const DEFAULT_THRESHOLDS = {
  http_req_failed: ['rate<0.01'],       // less than 1% errors
  http_req_duration: ['p(95)<2000'],    // p95 under 2s (CRUD should be fast)
};

// Reusable headers builder — call this with your token
export function authHeaders(token) {
  return {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };
}
// Load test: ramp up to realistic concurrency, hold, ramp down
// Run this: k6 run k6/load_test.js
// Save results: k6 run --out json=k6/results/load_baseline.json k6/load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Trend, Rate } from 'k6/metrics';
import { BASE_URL, authHeaders } from './config.js';
import { getToken } from './helpers/auth.js';

// Custom metrics per module — lets you see which module is slowest
const expenseDuration = new Trend('expense_duration_ms', true);
const budgetDuration = new Trend('budget_duration_ms', true);
const incomeDuration = new Trend('income_duration_ms', true);
const dashboardDuration = new Trend('dashboard_duration_ms', true);
const errorRate = new Rate('error_rate');

export const options = {
  stages: [
    { duration: '30s', target: 50 },    // Ramp up
    { duration: '2m',  target: 50 },    // Hold — this is your baseline measurement window
    { duration: '30s', target: 100 },   // Push a bit higher
    { duration: '1m',  target: 100 },   // Hold at higher load
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<2000'],
    'expense_duration_ms': ['p(95)<1500'],
    'budget_duration_ms': ['p(95)<1500'],
    'income_duration_ms': ['p(95)<1500'],
    'dashboard_duration_ms': ['p(95)<1500'],
    'error_rate': ['rate<0.01'],
  },
};

export function setup() {
  return { token: getToken() };
}

export default function (data) {
  const params = authHeaders(data.token);

  // Each VU rotates through modules — simulates real mixed usage
  // __ITER is the iteration count for this VU (0, 1, 2, 3...)
  const scenario = __ITER % 4;

  if (scenario === 0) {
    // Dashboard read-heavy flow
    const month = 4;
    const year = 2026;
    const start = Date.now();
    const res = http.get(`${BASE_URL}/dashboard/?month=${month}&year=${year}`, params);
    dashboardDuration.add(Date.now() - start);

    const ok = check(res, { 'dashboard object ok': (r) => r.status === 200 });
    errorRate.add(!ok);

  } else if (scenario === 1) {
    // Budget flow
    const start = Date.now();
    const res = http.get(`${BASE_URL}/budgets`, params);
    budgetDuration.add(Date.now() - start);

    const ok = check(res, { 'budget list ok': (r) => r.status === 200 });
    errorRate.add(!ok);

  } else if (scenario === 2) {
    // Income flow
    const start = Date.now();
    const res = http.get(`${BASE_URL}/incomes`, params);
    incomeDuration.add(Date.now() - start);

    const ok = check(res, { 'income list ok': (r) => r.status === 200 });
    errorRate.add(!ok);
  } else {
    // Expense flow
    const start = Date.now();
    const res = http.get(`${BASE_URL}/expenses`, params);
    expenseDuration.add(Date.now() - start);

    const ok = check(res, { 'expense list ok': (r) => r.status === 200 });
    errorRate.add(!ok);
  }

  sleep(1);
}
// Smoke test: 1 VU, just verifies every module responds correctly
// Run this: k6 run k6/smoke_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, authHeaders, DEFAULT_THRESHOLDS } from './config.js';
import { getToken } from './helpers/auth.js';

export const options = {
  vus: 1,
  duration: '30s',
  thresholds: DEFAULT_THRESHOLDS,
};

// setup() runs ONCE before the test — perfect for login
// Whatever you return here gets passed as `data` to default function
export function setup() {
  const token = getToken();
  console.log('Login successful, token acquired');
  return { token };
}

export default function (data) {
  const params = authHeaders(data.token);

  // ── EXPENSES ──────────────────────────────────────────
  const expenseList = http.get(`${BASE_URL}/expenses`, params);
  check(expenseList, {
    '[expense] GET list - status 200': (r) => r.status === 200,
    '[expense] GET list - returns array': (r) => Array.isArray(r.json()),
  });

  // Create an expense
  const newExpense = http.post(`${BASE_URL}/expenses`, JSON.stringify({
    amount: 50.00,
    category_id: 1,          // ← adjust field names to match your schema
    description: 'K6 test expense',
    date: '2024-01-15',
  }), params);
  check(newExpense, {
    '[expense] POST - status 201': (r) => r.status === 201,
    '[expense] POST - has id': (r) => r.json('id') !== undefined,
  });

  // Grab the created ID for subsequent operations
  const expenseId = newExpense.json('id');

  // Read it back
  const expenseGet = http.get(`${BASE_URL}/expenses/${expenseId}`, params);
  check(expenseGet, {
    '[expense] GET by id - status 200': (r) => r.status === 200,
    '[expense] GET by id - correct id': (r) => r.json('id') === expenseId,
  });

  // Update it
  const expenseUpdate = http.patch(`${BASE_URL}/expenses/${expenseId}`, JSON.stringify({
    amount: 75.00,
    description: 'K6 test expense - updated',
  }), params);
  check(expenseUpdate, {
    '[expense] PATCH - status 200': (r) => r.status === 200,
  });

  // Delete it (clean up after yourself — don't pollute test DB)
  const expenseDelete = http.del(`${BASE_URL}/expenses/${expenseId}`, null, params);
  check(expenseDelete, {
    '[expense] DELETE - status 200 or 204': (r) => [200, 204].includes(r.status),
  });

  sleep(0.5);

  // ── BUDGET ────────────────────────────────────────────
  const budgetList = http.get(`${BASE_URL}/budgets`, params);
  check(budgetList, {
    '[budget] GET list - status 200': (r) => r.status === 200,
  });

  sleep(0.5);

  // ── CATEGORY ──────────────────────────────────────────
  const categoryList = http.get(`${BASE_URL}/categories`, params);
  check(categoryList, {
    '[category] GET list - status 200': (r) => r.status === 200,
  });

  sleep(0.5);

  // ── INCOME ────────────────────────────────────────────
  const incomeList = http.get(`${BASE_URL}/incomes`, params);
  check(incomeList, {
    '[income] GET list - status 200': (r) => r.status === 200,
  });

  sleep(1);
}
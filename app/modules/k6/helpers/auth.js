import http from 'k6/http';
import { BASE_URL } from '../config.js';

// Call this inside setup() — runs once before the whole test
// Returns the token which K6 passes to every VU
export function getToken() {
  const res = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: 'kristen05@example.net',
    password: 'password123',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  if (res.status !== 200) {
    throw new Error(`Login failed: ${res.status} ${res.body}`);
  }

  // Adjust this based on what your auth endpoint actually returns
  // Common patterns:
  //   res.json('access_token')
  //   res.json('token')
  //   res.json('data.token')
  return res.json('auth.access_token');
}
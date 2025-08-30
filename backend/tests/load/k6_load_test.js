/**
 * k6 Load Testing Script for Baymax Backend
 * Run with: k6 run tests/load/k6_load_test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';
import ws from 'k6/ws';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 20 },    // Stay at 20 users
    { duration: '30s', target: 50 },   // Ramp up to 50 users
    { duration: '2m', target: 50 },    // Stay at 50 users
    { duration: '30s', target: 100 },  // Ramp up to 100 users
    { duration: '2m', target: 100 },   // Stay at 100 users
    { duration: '1m', target: 200 },   // Spike to 200 users
    { duration: '2m', target: 200 },   // Stay at 200 users (target)
    { duration: '2m', target: 0 },     // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'], // 95% of requests must complete below 1.5s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],               // Custom error rate below 10%
  },
};

const BASE_URL = 'http://localhost:8000';
const API_PATH = '/api/v1';

// Helper function to get auth token
function getAuthToken() {
  const loginPayload = JSON.stringify({
    username: 'doctor@example.com',
    password: 'Test@1234',
  });

  const loginRes = http.post(`${BASE_URL}${API_PATH}/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });

  if (loginRes.status === 200) {
    return JSON.parse(loginRes.body).access_token;
  }
  return null;
}

export function setup() {
  // Setup code - create test data if needed
  return { token: getAuthToken() };
}

export default function (data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': data.token ? `Bearer ${data.token}` : '',
  };

  // Scenario 1: Health checks
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 500ms': (r) => r.timings.duration < 500,
  });

  // Scenario 2: Patient search
  const patientsRes = http.get(`${BASE_URL}${API_PATH}/patients/`, { headers });
  check(patientsRes, {
    'patients list status is 200': (r) => r.status === 200,
    'patients response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  errorRate.add(patientsRes.status !== 200);

  // Scenario 3: Appointment availability check
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const providerId = '00000000-0000-0000-0000-000000000000';
  
  const slotsRes = http.get(
    `${BASE_URL}${API_PATH}/appointments/slots/available?provider_id=${providerId}&date=${tomorrow.toISOString()}&appointment_type=physical`,
    { headers }
  );
  check(slotsRes, {
    'slots check status is 200': (r) => r.status === 200,
    'slots response time < 1500ms': (r) => r.timings.duration < 1500,
  });

  // Scenario 4: Create patient (write operation)
  if (Math.random() < 0.2) { // 20% of users create patients
    const patientPayload = JSON.stringify({
      phone: `9876${Math.floor(Math.random() * 1000000)}`,
      email: `patient${Math.floor(Math.random() * 10000)}@example.com`,
      first_name: 'Load',
      last_name: 'Test',
      date_of_birth: '1990-01-01',
      gender: 'male',
    });

    const createPatientRes = http.post(
      `${BASE_URL}${API_PATH}/patients/`,
      patientPayload,
      { headers }
    );
    check(createPatientRes, {
      'patient creation status is 200 or 400': (r) => r.status === 200 || r.status === 400,
    });
  }

  sleep(1);
}

// WebSocket test scenario
export function testWebSocket() {
  const sessionId = `k6_test_${Math.floor(Math.random() * 10000)}`;
  const url = `ws://localhost:8000${API_PATH}/intake/ws/${sessionId}`;

  const res = ws.connect(url, {}, function (socket) {
    socket.on('open', () => {
      console.log('WebSocket connected');
      
      // Send initial message
      socket.send(JSON.stringify({
        type: 'text_message',
        content: 'I have knee pain',
        language: 'en',
      }));
    });

    socket.on('message', (data) => {
      const message = JSON.parse(data);
      check(message, {
        'WebSocket response has type': (m) => m.type !== undefined,
        'WebSocket response has content': (m) => m.content !== undefined || m.message !== undefined,
      });

      // Send follow-up message
      if (message.type === 'ai_response') {
        socket.send(JSON.stringify({
          type: 'text_message',
          content: 'It hurts when I walk',
          language: 'en',
        }));
      }

      // End session after a few exchanges
      socket.setTimeout(() => {
        socket.send(JSON.stringify({
          type: 'end_session',
        }));
        socket.close();
      }, 5000);
    });

    socket.on('error', (e) => {
      console.error('WebSocket error:', e);
      errorRate.add(1);
    });
  });

  check(res, {
    'WebSocket connection successful': (r) => r && r.status === 101,
  });
}

// Stress test scenario
export function stressTest() {
  const responses = http.batch([
    ['GET', `${BASE_URL}/health`],
    ['GET', `${BASE_URL}/health/ready`],
    ['GET', `${BASE_URL}${API_PATH}/patients/`],
    ['GET', `${BASE_URL}${API_PATH}/appointments/`],
    ['GET', `${BASE_URL}${API_PATH}/providers/`],
  ]);

  responses.forEach((res) => {
    check(res, {
      'batch request status < 500': (r) => r.status < 500,
    });
    errorRate.add(res.status >= 500);
  });
}

export function teardown(data) {
  // Cleanup code if needed
  console.log('Load test completed');
}
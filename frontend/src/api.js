/**
 * EVE Healthcare — API client
 * All calls go to the FastAPI backend at http://localhost:8000
 */

const BASE_URL = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('token');
}

async function request(method, path, body = null, auth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(`${BASE_URL}${path}`, options);
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = data?.detail || `HTTP ${res.status}`;
    throw new Error(typeof msg === 'string' ? msg : JSON.stringify(msg));
  }
  return data;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export async function signup(name, email, password) {
  return request('POST', '/auth/signup', { name, email, password });
}

export async function login(email, password) {
  return request('POST', '/auth/login', { email, password });
}

export async function getMe() {
  return request('GET', '/auth/me', null, true);
}

// ── Centres ───────────────────────────────────────────────────────────────────

export async function getCentres(page = 1, pageSize = 100) {
  return request('GET', `/centres?page=${page}&page_size=${pageSize}`);
}

// ── Tests ─────────────────────────────────────────────────────────────────────

export async function getTests(centreId = null, page = 1, pageSize = 100) {
  const qs = centreId ? `?centre_id=${centreId}&page=${page}&page_size=${pageSize}` : `?page=${page}&page_size=${pageSize}`;
  return request('GET', `/tests${qs}`);
}

// ── Bookings ──────────────────────────────────────────────────────────────────

export async function createBooking(testId, centreId, appointmentTime) {
  return request('POST', '/bookings', { test_id: testId, centre_id: centreId, appointment_time: appointmentTime }, true);
}

export async function getBookings(page = 1, pageSize = 20) {
  return request('GET', `/bookings?page=${page}&page_size=${pageSize}`, null, true);
}

export async function cancelBooking(bookingId) {
  return request('PATCH', `/bookings/${bookingId}/cancel`, null, true);
}

// ── Payments ──────────────────────────────────────────────────────────────────

export async function initiatePayment(bookingId) {
  return request('POST', '/payments', { booking_id: bookingId }, true);
}

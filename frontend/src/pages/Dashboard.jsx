import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  getMe,
  getBookings,
  getCentres,
  getTests,
  createBooking,
  cancelBooking,
  initiatePayment,
} from '../api';
import './Dashboard.css';

/* ─── helpers ──────────────────────────────────────────────────────────────── */
function fmt(isoString) {
  if (!isoString) return '—';
  const d = new Date(isoString);
  return d.toLocaleString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function statusClass(s) {
  return s?.toLowerCase() || '';
}

/* ─── Dashboard ────────────────────────────────────────────────────────────── */
const Dashboard = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('bookings');

  /* Auth / user state */
  const [user, setUser]         = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  /* Bookings list */
  const [bookings, setBookings]   = useState([]);
  const [bookLoading, setBookLoading] = useState(false);
  const [bookError, setBookError]   = useState('');

  /* Payment actions */
  const [actionLoading, setActionLoading] = useState({});
  const [actionMsg, setActionMsg]         = useState('');

  /* New-booking form state */
  const [centres, setCentres]       = useState([]);
  const [tests, setTests]           = useState([]);
  const [selCentreId, setSelCentreId] = useState('');
  const [selTestId, setSelTestId]   = useState('');
  const [apptDate, setApptDate]     = useState('');
  const [apptTime, setApptTime]     = useState('');
  const [formError, setFormError]   = useState('');
  const [formLoading, setFormLoading] = useState(false);
  const [formSuccess, setFormSuccess] = useState('');

  /* ── Load user on mount ──────────────────────────────────────────────────── */
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) { navigate('/login'); return; }
    getMe()
      .then(setUser)
      .catch(() => { localStorage.removeItem('token'); navigate('/login'); })
      .finally(() => setAuthLoading(false));
  }, [navigate]);

  /* ── Load bookings whenever Bookings tab is active ───────────────────────── */
  const fetchBookings = useCallback(async () => {
    setBookLoading(true);
    setBookError('');
    try {
      const res = await getBookings();
      setBookings(res.items || []);
    } catch (e) {
      setBookError(e.message || 'Failed to load bookings.');
    } finally {
      setBookLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === 'bookings' && user) fetchBookings();
  }, [activeTab, user, fetchBookings]);

  /* ── Load centres when Book tab becomes active ───────────────────────────── */
  useEffect(() => {
    if (activeTab === 'book') {
      getCentres().then(r => setCentres(r.items || [])).catch(() => {});
      setSelCentreId(''); setSelTestId(''); setTests([]);
      setFormError(''); setFormSuccess('');
    }
  }, [activeTab]);

  /* ── Load tests when a centre is selected ────────────────────────────────── */
  useEffect(() => {
    if (selCentreId) {
      getTests(selCentreId).then(r => setTests(r.items || [])).catch(() => setTests([]));
      setSelTestId('');
    } else {
      setTests([]);
    }
  }, [selCentreId]);

  /* ── Handlers ────────────────────────────────────────────────────────────── */
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  const handlePay = async (bookingId) => {
    setActionLoading(p => ({ ...p, [bookingId]: 'paying' }));
    setActionMsg('');
    try {
      const payment = await initiatePayment(bookingId);
      setActionMsg(
        payment.status === 'SUCCESS'
          ? '✅ Payment successful! Booking confirmed.'
          : '❌ Payment failed. You can try again or cancel.',
      );
      fetchBookings();
    } catch (e) {
      setActionMsg(`⚠️ ${e.message}`);
    } finally {
      setActionLoading(p => ({ ...p, [bookingId]: null }));
    }
  };

  const handleCancel = async (bookingId) => {
    if (!window.confirm('Cancel this booking?')) return;
    setActionLoading(p => ({ ...p, [bookingId]: 'cancelling' }));
    setActionMsg('');
    try {
      await cancelBooking(bookingId);
      setActionMsg('Booking cancelled.');
      fetchBookings();
    } catch (e) {
      setActionMsg(`⚠️ ${e.message}`);
    } finally {
      setActionLoading(p => ({ ...p, [bookingId]: null }));
    }
  };

  const handleBookSubmit = async (e) => {
    e.preventDefault();
    setFormError(''); setFormSuccess('');
    if (!selCentreId || !selTestId || !apptDate || !apptTime) {
      setFormError('Please fill in all fields.'); return;
    }
    const dt = new Date(`${apptDate}T${apptTime}:00`);
    if (dt <= new Date()) {
      setFormError('Appointment must be in the future.'); return;
    }
    setFormLoading(true);
    try {
      // Send ISO 8601 with local offset
      const offset = -dt.getTimezoneOffset();
      const sign   = offset >= 0 ? '+' : '-';
      const pad    = n => String(Math.floor(Math.abs(n))).padStart(2, '0');
      const tz     = `${sign}${pad(offset / 60)}:${pad(offset % 60)}`;
      const iso    = `${apptDate}T${apptTime}:00${tz}`;

      await createBooking(selTestId, selCentreId, iso);
      setFormSuccess('✅ Booking created! Proceed to My Bookings to pay.');
      setSelCentreId(''); setSelTestId(''); setApptDate(''); setApptTime('');
    } catch (e) {
      setFormError(e.message || 'Failed to create booking.');
    } finally {
      setFormLoading(false);
    }
  };

  /* ── Render ──────────────────────────────────────────────────────────────── */
  if (authLoading) {
    return (
      <div className="dashboard-loader">
        <div className="loader-spinner" />
        <p>Loading…</p>
      </div>
    );
  }

  const selectedTest = tests.find(t => t.id === selTestId);

  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <h2><span className="text-gradient">EVE</span></h2>
          <p className="sidebar-subtitle">Healthcare</p>
        </div>
        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activeTab === 'bookings' ? 'active' : ''}`}
            onClick={() => setActiveTab('bookings')}
          >
            <span className="nav-icon">📋</span>
            <span className="nav-label">My Bookings</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'book' ? 'active' : ''}`}
            onClick={() => setActiveTab('book')}
          >
            <span className="nav-icon">➕</span>
            <span className="nav-label">Book New Test</span>
          </button>
          <button
            className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <span className="nav-icon">👤</span>
            <span className="nav-label">Profile</span>
          </button>
        </nav>
        <div className="sidebar-footer">
          <button className="btn btn-secondary logout-btn" onClick={handleLogout}>
            Log Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="topbar">
          <h1>
            {activeTab === 'bookings' && 'My Bookings'}
            {activeTab === 'book'     && 'Book a Test'}
            {activeTab === 'profile'  && 'Profile'}
          </h1>
          <div className="topbar-right">
            {user && <span className="user-name">{user.name}</span>}
            <img
              src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || 'U')}&background=00d8ff&color=000`}
              alt="User avatar"
              className="user-avatar"
            />
          </div>
        </header>

        <div className="content-area">

          {/* ── BOOKINGS TAB ────────────────────────────────────────────── */}
          {activeTab === 'bookings' && (
            <div className="bookings-view animate-fade-in">
              {actionMsg && (
                <div className={`action-banner ${actionMsg.startsWith('✅') ? 'success' : actionMsg.startsWith('❌') ? 'fail' : 'warn'}`}>
                  {actionMsg}
                  <button className="banner-close" onClick={() => setActionMsg('')}>×</button>
                </div>
              )}

              <div className="section-header">
                <h2>Your Appointments</h2>
                <button className="btn btn-secondary btn-sm" onClick={fetchBookings} disabled={bookLoading}>
                  {bookLoading ? 'Refreshing…' : '↻ Refresh'}
                </button>
              </div>

              {bookLoading && (
                <div className="loading-state">
                  <div className="loader-spinner" />
                  <p>Loading bookings…</p>
                </div>
              )}

              {!bookLoading && bookError && (
                <div className="empty-state error-state">
                  <p>⚠️ {bookError}</p>
                  <button className="btn btn-primary btn-sm" onClick={fetchBookings}>Retry</button>
                </div>
              )}

              {!bookLoading && !bookError && bookings.length === 0 && (
                <div className="empty-state">
                  <div className="empty-icon">🩺</div>
                  <h3>No bookings yet</h3>
                  <p>Click <strong>Book New Test</strong> to schedule your first appointment.</p>
                  <button className="btn btn-primary" onClick={() => setActiveTab('book')}>
                    Book Now
                  </button>
                </div>
              )}

              {!bookLoading && bookings.length > 0 && (
                <div className="bookings-grid">
                  {bookings.map((b) => (
                    <div key={b.id} className="booking-card glass-card">
                      <div className="booking-header">
                        <span className="booking-id">#{b.id.slice(0, 8).toUpperCase()}</span>
                        <span className={`status ${statusClass(b.status)}`}>{b.status}</span>
                      </div>
                      <div className="booking-body">
                        <h3>{b.test_name || 'Diagnostic Test'}</h3>
                        <p className="centre-name">📍 {b.centre_name || 'Diagnostic Centre'}</p>
                        <div className="booking-details">
                          <div className="detail-item">
                            <span>Appointment</span>
                            <strong>{fmt(b.appointment_time)}</strong>
                          </div>
                          <div className="detail-item">
                            <span>Amount</span>
                            <strong>₹{parseFloat(b.amount).toFixed(2)}</strong>
                          </div>
                        </div>
                      </div>
                      {b.status === 'PENDING' && (
                        <div className="booking-actions">
                          <button
                            className="btn btn-primary btn-sm"
                            disabled={!!actionLoading[b.id]}
                            onClick={() => handlePay(b.id)}
                          >
                            {actionLoading[b.id] === 'paying' ? 'Processing…' : 'Pay Now'}
                          </button>
                          <button
                            className="btn btn-secondary btn-sm"
                            disabled={!!actionLoading[b.id]}
                            onClick={() => handleCancel(b.id)}
                          >
                            {actionLoading[b.id] === 'cancelling' ? 'Cancelling…' : 'Cancel'}
                          </button>
                        </div>
                      )}
                      {b.status === 'CONFIRMED' && (
                        <div className="booking-actions">
                          <button
                            className="btn btn-danger btn-sm"
                            disabled={!!actionLoading[b.id]}
                            onClick={() => handleCancel(b.id)}
                          >
                            {actionLoading[b.id] === 'cancelling' ? 'Cancelling…' : 'Cancel Booking'}
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ── BOOK TAB ─────────────────────────────────────────────────── */}
          {activeTab === 'book' && (
            <div className="book-view animate-fade-in">
              <div className="glass-card book-form-card">
                <h2>Schedule a Diagnostic Test</h2>
                <p className="form-subtitle">Choose a centre, test, and appointment slot.</p>

                {formError   && <div className="form-msg error">{formError}</div>}
                {formSuccess  && <div className="form-msg success">{formSuccess}</div>}

                <form className="auth-form" onSubmit={handleBookSubmit}>
                  {/* Centre */}
                  <div className="form-group">
                    <label>Diagnostic Centre</label>
                    <select
                      className="custom-select"
                      value={selCentreId}
                      onChange={e => setSelCentreId(e.target.value)}
                      required
                      disabled={formLoading}
                    >
                      <option value="">— Choose Centre —</option>
                      {centres.map(c => (
                        <option key={c.id} value={c.id}>{c.name} — {c.location}</option>
                      ))}
                    </select>
                    {centres.length === 0 && (
                      <p className="hint">No centres found. Ask an admin to add some via the API.</p>
                    )}
                  </div>

                  {/* Test */}
                  <div className="form-group">
                    <label>Diagnostic Test</label>
                    <select
                      className="custom-select"
                      value={selTestId}
                      onChange={e => setSelTestId(e.target.value)}
                      required
                      disabled={formLoading || !selCentreId}
                    >
                      <option value="">— Choose Test —</option>
                      {tests.map(t => (
                        <option key={t.id} value={t.id}>
                          {t.name} — ₹{parseFloat(t.price).toFixed(2)}
                        </option>
                      ))}
                    </select>
                    {selCentreId && tests.length === 0 && (
                      <p className="hint">No tests available for this centre.</p>
                    )}
                  </div>

                  {/* Price preview */}
                  {selectedTest && (
                    <div className="price-preview glass-card">
                      <span className="price-label">Total Amount</span>
                      <span className="price-value">₹{parseFloat(selectedTest.price).toFixed(2)}</span>
                    </div>
                  )}

                  {/* Date & Time */}
                  <div className="form-row">
                    <div className="form-group">
                      <label>Appointment Date</label>
                      <input
                        type="date"
                        value={apptDate}
                        onChange={e => setApptDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        required
                        disabled={formLoading}
                      />
                    </div>
                    <div className="form-group">
                      <label>Time Slot</label>
                      <input
                        type="time"
                        value={apptTime}
                        onChange={e => setApptTime(e.target.value)}
                        required
                        disabled={formLoading}
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn btn-primary"
                    style={{ marginTop: '1rem', width: '100%' }}
                    disabled={formLoading}
                  >
                    {formLoading ? 'Creating Booking…' : 'Confirm Booking'}
                  </button>
                </form>
              </div>
            </div>
          )}

          {/* ── PROFILE TAB ──────────────────────────────────────────────── */}
          {activeTab === 'profile' && (
            <div className="profile-view animate-fade-in">
              <div className="glass-card profile-card">
                <div className="profile-avatar-wrap">
                  <img
                    src={`https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || 'U')}&background=00d8ff&color=000&size=128`}
                    alt="Avatar"
                    className="profile-avatar"
                  />
                </div>
                <h2>{user?.name}</h2>
                <p className="profile-email">{user?.email}</p>
                <div className="profile-meta">
                  <div className="meta-item">
                    <span>Member Since</span>
                    <strong>{user?.created_at ? new Date(user.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' }) : '—'}</strong>
                  </div>
                  <div className="meta-item">
                    <span>Total Bookings</span>
                    <strong>{bookings.length}</strong>
                  </div>
                </div>
                <button className="btn btn-secondary" onClick={handleLogout} style={{ marginTop: '2rem' }}>
                  Log Out
                </button>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
};

export default Dashboard;

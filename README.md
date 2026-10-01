# EVE Healthcare — Diagnostic Booking & Payment Backend

> **EVE Healthcare SDE Intern Assignment** | FastAPI · PostgreSQL · JWT · Docker

A production-grade backend service for diagnostic test bookings and simulated payments, built with **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Docker Compose**.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Running Locally (Frontend)](#running-locally-frontend)
3. [Running Locally (Backend without Docker)](#running-locally-backend-without-docker)
4. [Running with Docker (Backend)](#running-with-docker-backend)
5. [Running Tests](#running-tests)
6. [API Endpoints](#api-endpoints)
7. [Example Requests](#example-requests)
8. [Database / Schema Design](#database--schema-design)
9. [Architecture](#architecture)
10. [Idempotency Design](#idempotency-design)
11. [Assumptions](#assumptions)
12. [What I Would Improve](#what-i-would-improve)

---

## Quick Start

```bash
# Clone the repo
git clone <your-repo-url>
cd EVE-Assignment

# 1. Start the Backend (with Docker)
cp backend/.env.example backend/.env
docker-compose up --build -d

# 2. Start the Frontend (Vite + React)
cd frontend
npm install
npm run dev
```

Backend API is now running at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**  
Frontend UI is now running at **http://localhost:5173**

---

## Running Locally (Frontend)

The frontend is a modern React application built with Vite and vanilla CSS (no Tailwind per assignment guidelines). It features a premium, responsive dark-mode UI with a landing page, authentication screens, and a user dashboard.

```bash
cd frontend
npm install
npm run dev
```

Open your browser to `http://localhost:5173`.

---

## Running Locally (Backend without Docker)

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ running locally

### Steps

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local Postgres

# Run the app (tables are auto-created on startup)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Running with Docker

```bash
# Build and start all services (PostgreSQL + Redis + API)
docker-compose up --build

# Run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Stop everything
docker-compose down
```

---

## Running Tests

Tests use **SQLite in-memory** — no running PostgreSQL required.

```bash
cd backend

# Install deps (if not already done)
pip install -r requirements.txt

# Run all tests
pytest -v

# Run with coverage
pytest -v --cov=app --cov-report=term-missing
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | ❌ | Register a new user |
| POST | `/auth/login` | ❌ | Login, receive JWT |
| GET | `/auth/me` | ✅ | Get current user profile |

### Diagnostic Centres

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/centres` | ❌ | List centres (paginated) |
| GET | `/centres/{id}` | ❌ | Get centre with its tests |
| POST | `/centres` | ❌ | Create a centre |

### Diagnostic Tests

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/tests` | ❌ | List tests (filter by `?centre_id=`) |
| GET | `/tests/{id}` | ❌ | Get a single test |
| POST | `/tests` | ❌ | Create a test for a centre |

### Bookings

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/bookings` | ✅ | Create a booking (PENDING) |
| GET | `/bookings` | ✅ | List own bookings (paginated) |
| GET | `/bookings/{id}` | ✅ | Get a single booking |
| PATCH | `/bookings/{id}/cancel` | ✅ | Cancel a booking |

### Payments

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments` | ✅ | Initiate simulated payment |
| GET | `/payments/{id}` | ✅ | Get payment details |
| POST | `/payments/webhook` | ❌ | Webhook (idempotent) |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |

---

## Example Requests

### 1. Sign Up

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "securepass123"}'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "securepass123"}'
# Returns: {"access_token": "eyJ...", "token_type": "bearer"}
```

### 3. Create a Diagnostic Centre

```bash
curl -X POST http://localhost:8000/centres \
  -H "Content-Type: application/json" \
  -d '{"name": "EVE Diagnostics", "location": "Indore, MP"}'
```

### 4. Create a Diagnostic Test

```bash
curl -X POST http://localhost:8000/tests \
  -H "Content-Type: application/json" \
  -d '{
    "centre_id": "<centre-id>",
    "name": "Complete Blood Count",
    "description": "Full CBC panel",
    "price": "750.00"
  }'
```

### 5. Book a Test

```bash
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": "<test-id>",
    "centre_id": "<centre-id>",
    "appointment_time": "2026-11-01T10:00:00+05:30"
  }'
# Returns booking with status: "PENDING"
```

### 6. Initiate Payment

```bash
curl -X POST http://localhost:8000/payments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"booking_id": "<booking-id>"}'
# Returns payment with status: "SUCCESS" or "FAILED" (70/30 random)
# Booking is updated atomically to CONFIRMED or FAILED
```

### 7. Simulated Webhook

```bash
curl -X POST http://localhost:8000/payments/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "EVT-unique-123",
    "booking_id": "<booking-id>",
    "status": "SUCCESS",
    "amount": "750.00"
  }'
# Sending the same event_id twice returns the same 200 response (idempotent)
```

---

## Database / Schema Design

```
users
  ├── id (UUID, PK)
  ├── name
  ├── email (UNIQUE, indexed)
  ├── hashed_password
  └── created_at / updated_at

diagnostic_centres
  ├── id (UUID, PK)
  ├── name
  ├── location
  └── created_at / updated_at

diagnostic_tests
  ├── id (UUID, PK)
  ├── centre_id (FK → diagnostic_centres, indexed)
  ├── name
  ├── description
  ├── price (DECIMAL 10,2)
  └── created_at / updated_at

bookings
  ├── id (UUID, PK)
  ├── user_id (FK → users, indexed)
  ├── test_id (FK → diagnostic_tests)
  ├── centre_id (FK → diagnostic_centres)
  ├── appointment_time (TIMESTAMPTZ)
  ├── amount (DECIMAL 10,2)
  ├── status (ENUM: PENDING | CONFIRMED | FAILED | CANCELLED)
  └── created_at / updated_at

payments
  ├── id (UUID, PK)
  ├── booking_id (FK → bookings, indexed)
  ├── event_id (UNIQUE, indexed) ← idempotency key
  ├── amount (DECIMAL 10,2)
  ├── status (ENUM: SUCCESS | FAILED)
  └── created_at
```

### Relationships

```
User ──< Booking >── DiagnosticTest ──< DiagnosticCentre
Booking ──< Payment
```

### Key Design Decisions

- **UUID primary keys** — avoids sequential ID enumeration attacks  
- **UNIQUE constraint on `payments.event_id`** — database-level idempotency guarantee  
- **DECIMAL(10, 2)** for all monetary values — avoids floating-point precision issues  
- **TIMESTAMPTZ** for all datetime columns — timezone-aware storage  
- **Indexes** on all FK and frequently-queried columns  

---

## Architecture

```
Client (Postman / Frontend)
         │
         ▼
    FastAPI API Layer
         │
    ┌────┼────┐
    ▼    ▼    ▼
  Auth  Booking  Payment
    └────┼────┘
         ▼
   Service Layer (Business Logic)
         │
   Repository Layer (Data Access)
         │
         ▼
    PostgreSQL
```

### Project Structure

```
backend/
├── app/
│   ├── main.py               # FastAPI app factory
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── database.py       # SQLAlchemy engine + session
│   │   └── security.py       # JWT + bcrypt
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Pydantic request/response schemas
│   ├── api/                  # FastAPI routers
│   │   └── deps.py           # JWT auth dependency
│   ├── services/             # Business logic
│   └── repositories/         # Data access layer
├── tests/                    # Pytest test suite
├── alembic/                  # DB migrations
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

---

## Idempotency Design

The webhook endpoint uses a two-layer idempotency strategy:

**Layer 1 — Application check:**
```
Webhook arrives with event_id = "EVT-123"
          │
          ▼
Does payment with event_id exist in DB?
     YES → return 200 "already processed"
     NO  → proceed to process
```

**Layer 2 — Database constraint:**
```sql
UNIQUE CONSTRAINT payments.event_id
```

This handles concurrent duplicate deliveries that bypass Layer 1 — the DB insert will raise an `IntegrityError` which prevents double-processing.

Both layers together guarantee: **same event_id → at-most-once processing**.

---

## Booking State Machine

```
                  ┌─────────┐
                  │ PENDING │ ← created here
                  └────┬────┘
                       │
          ┌────────────┴────────────┐
          │ payment SUCCESS         │ payment FAILED
          ▼                         ▼
    ┌───────────┐             ┌────────┐
    │ CONFIRMED │             │ FAILED │
    └─────┬─────┘             └────────┘
          │
          │ user cancels
          ▼
    ┌───────────┐
    │ CANCELLED │
    └───────────┘
```

---

## Assumptions

1. **No admin roles** — centre/test creation is open (no auth). In production this would be behind an admin role.
2. **Single payment per booking** — once a booking is paid (CONFIRMED or FAILED), a second `POST /payments` is rejected.
3. **Appointment time must be in the future** — and must include timezone info.
4. **Test-centre consistency** — booking validates that the chosen test belongs to the chosen centre.
5. **Simulated payment** — 70% SUCCESS, 30% FAILED probability. In production this would be replaced by a real gateway (Razorpay, Stripe etc.).
6. **Tables auto-created** on startup via `Base.metadata.create_all`. In production, Alembic migrations should be the only mechanism.
7. **Webhook has no authentication** — in production, webhook signatures (e.g., HMAC-SHA256) should be verified.

---

## What I Would Improve

| Area | Improvement |
|------|-------------|
| **Auth** | Add role-based access control (admin vs. patient) |
| **Webhook security** | Verify HMAC-SHA256 signature from provider |
| **Migrations** | Use Alembic exclusively; remove `create_all` from startup |
| **Caching** | Cache `/centres` and `/tests` responses in Redis |
| **Background jobs** | Celery task for payment retries and booking reminders |
| **Rate limiting** | Per-IP limits on `/auth/login` to prevent brute force |
| **Observability** | OpenTelemetry traces + Prometheus metrics |
| **Pagination cursor** | Cursor-based pagination for large datasets (vs. offset) |
| **Integration tests** | Test against real PostgreSQL in CI (GitHub Actions + service containers) |
| **Soft deletes** | Add `deleted_at` column instead of hard deletes |

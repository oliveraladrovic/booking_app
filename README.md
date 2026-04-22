# Booking API

A backend API for managing users, services, and bookings with real-world business rules, built using FastAPI and SQLAlchemy.

**Live API Docs:**
https://booking-app-3plw.onrender.com/docs
> Note: The app is hosted on a free tier and may take a few seconds to wake up.
---

## Overview

This project is a backend application that simulates a real-world booking system (e.g. dental clinic, barber, etc.).

The focus is not just CRUD operations, but enforcing **business rules** such as:

* Preventing overlapping bookings
* Managing booking lifecycle (pending → confirmed → completed/cancelled)
* Validating time constraints and data integrity

---

## Features

### Users

* Create user
* List users
* Get user by ID
* Update user (partial update)
* Soft delete (anonymization + deactivation)

---

### Services

* Create service
* List services
* Get service by ID
* Update service
* Soft delete (deactivation)

---

### Bookings

* Create booking with automatic time calculation
* Prevent overlapping bookings (single-capacity system)
* Enforce booking lifecycle:

  * `pending → confirmed`
  * `confirmed → completed`
  * `pending/confirmed → cancelled`
* Validate:

  * user and service existence
  * active status
  * start time (cannot be in the past)

---

## Business Logic Highlights

* **Single-capacity scheduling model**
  Only one active booking can exist at a given time slot.

* **Automatic end time calculation**
  Based on service duration.

* **Strict lifecycle control**
  Invalid state transitions are prevented.

---

## Tech Stack

* **FastAPI** – API framework
* **SQLAlchemy 2.0** – ORM
* **PostgreSQL** – Database
* **Alembic** – Migrations
* **Pydantic v2** – Data validation
* **Pytest** – Testing
* **Docker** – Containerization
* **Render** – Deployment

## Development & Tooling
- **Poetry** – dependency management
- **GitHub Actions** – CI
---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/oliveraladrovic/booking_app.git
cd booking_app
```

---

### 2. Create `.env`

Copy the example file:

```bash
cp .env.example .env
```
Then update the database connection strings:
- DATABASE_URL → your local development database
- TEST_DATABASE_URL → your local test database

---

### 3. Install dependencies

```bash
poetry install
```

---

### 4. Run migrations

```bash
poetry run alembic upgrade head
```

---

### 5. Start the application

```bash
poetry run uvicorn booking_app.main:app --reload
```

---

### 6. Open docs

http://127.0.0.1:8000/docs

---

## Run with Docker

### Build image

```bash
docker build -t booking-app .
```

---

### Create `.env.docker`

Copy environment file:

```bash
cp .env.example.docker .env.docker
```
Then update:
- DATABASE_URL → must point to a reachable database from inside Docker

---
### Run container

```bash
docker run --rm -p 8000:8000 --env-file .env.docker booking-app
```

---

### Open API

http://127.0.0.1:8000/docs

---

## Testing

Run tests locally:

```bash
poetry run pytest -v
```

---

## 🔄 CI

* GitHub Actions runs tests on every push
* Ensures application stability and correctness

---

## Project Structure

```text
alembic/
src/
  booking_app/
    api/
    models/
    schemas/
    services/
    db/
    shared/
    config.py
    main.py
tests/
```

---

## What This Project Demonstrates

* Clean backend architecture (API → Service → DB)
* Real-world business logic implementation
* REST API design best practices
* Environment-based configuration
* Dockerized application setup
* CI integration with automated testing

---



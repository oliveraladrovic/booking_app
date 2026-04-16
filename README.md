# Booking App (Backend)

Simple backend application for managing users, services, and bookings.
Built with FastAPI, SQLAlchemy, PostgreSQL, and tested with pytest.

## Features (current)

* Create user
* Email validation
* Duplicate email handling
* Global error handling
* PostgreSQL test setup
* CI with GitHub Actions

## Tech stack

* FastAPI
* SQLAlchemy
* PostgreSQL
* pytest
* Poetry

## Run locally

```
poetry install
poetry run uvicorn booking_app.main:app --reload
```

## Run tests

```
poetry run pytest
```

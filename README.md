# Finance Tracker

Personal finance ingestion + analytics platform built as a Python interview-prep portfolio project. Two-service architecture: **Flask** handles CSV ingestion (pandas pipeline + fuzzy-merchant dedup); **Django/DRF** is the system of record (CRUD API + recurring-transaction analytics endpoint).

## Architecture

```
       ┌──────────────┐  multipart CSV   ┌──────────────┐
       │              │ ───────────────▶ │   Flask      │
       │              │                  │ /ingest/csv  │
       │              │                  └──────┬───────┘
       │              │                         │ X-Internal-Key
       │   client     │                         ▼
       │   (curl,     │                  ┌──────────────┐
       │   browser)   │  Token auth      │  Django/DRF  │ ←─── Postgres
       │              │ ◀──────────────▶ │  /api/...    │
       └──────────────┘                  └──────────────┘
```

- **Flask** parses bank CSVs, normalizes the schema, cleans merchant strings, and uses RapidFuzz to dedup against Django's recent transactions before forwarding survivors.
- **Django** owns persistence. Public REST API (token auth, multi-tenant queryset filtering) and an internal API (shared-secret auth) used only by Flask.
- **Postgres** is the only durable store; only Django writes to it.
- **Trust boundary** is real — Flask authenticates to Django with a shared `X-Internal-Key`, not a user token.

## Stack

Python 3.12 · Django 4.2 + DRF · Flask 3 · Postgres 16 · pandas · numpy · RapidFuzz · pytest · pytest-django · factory-boy · requests-mock · docker-compose.

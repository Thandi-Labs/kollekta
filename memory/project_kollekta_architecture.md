---
name: project-kollekta-architecture
description: Architecture and design decisions for the Kollekta M-Pesa Daraja payment microservice
metadata:
  type: project
---

Kollekta is a FastAPI microservice that integrates with the Safaricom M-Pesa Daraja API. It collects payments from customers (C2B / STK Push) and disburses to recipients (B2C). Only payment data is stored — no auth, user, or client management.

**Why:** Single-responsibility microservice for payment collection and disbursement via M-Pesa Daraja.

**How to apply:** Keep the scope strictly to payment data. Any client/user management belongs in a separate service.

## Key files
- `src/config.py` — Pydantic Settings, reads from `.env`
- `src/database.py` — SQLAlchemy sync engine, `get_db` dependency
- `src/models/payment.py` — Three models: `STKTransaction`, `C2BTransaction`, `B2CTransaction`
- `src/schemas/mpesa.py` — Daraja request/callback Pydantic models
- `src/schemas/payment.py` — API response schemas
- `src/services/daraja.py` — HTTP client for Daraja (auth, STK push, C2B register, B2C)
- `src/routes/stk.py` — POST /api/v1/stk/push + callback
- `src/routes/c2b.py` — POST /api/v1/c2b/register + validation + confirmation
- `src/routes/b2c.py` — POST /api/v1/b2c/disburse + result + timeout
- `src/routes/payments.py` — GET queries for all three transaction types
- `alembic/` — DB migrations; env.py reads DATABASE_URL from settings

## Env vars required
See `.env.example` — needs MPESA_* credentials from Daraja developer portal and a public MPESA_CALLBACK_BASE_URL for Daraja to call back.

## Transaction statuses
- STK/B2C: `pending` → `success`/`failed` (STK) or `completed`/`failed` (B2C)
- C2B: no status field — confirmation callback creates the record directly

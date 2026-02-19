Invio is a smart inventory management system for small retailers. This repository contains the backend API that powers:

- Product & barcode catalog
- Stock movements (IN/OUT/ADJUST)
- Stores & users (RBAC)
- Low-stock alerts + analytics-ready endpoints
- Mobile offline sync (scan events batching)

---

## Features

- Multi-store inventory model
- Product management with barcode support (EAN/UPC/QR)
- Stock ledger (immutable stock movements)
- Audit trail ready (who changed what, when)
- Scan event ingestion for mobile devices (offline sync)
- Health check + structured logging

## Start the api

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

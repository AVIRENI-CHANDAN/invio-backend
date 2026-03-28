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

Install dependencies into your project environment first:

```bash
venv\Scripts\python -m pip install -r requirements.txt
```

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You can also start it by executing the entrypoint file directly:

```bash
python app/main.py
```

## Run tests

Run the test suite from the repository root:

```bash
venv\Scripts\python -m unittest discover -s tests -v
```

If your IDE shows import errors during test collection, make sure it is using the project interpreter:

```bash
d:\Invio\backend\venv\Scripts\python.exe
```

Or install the dependencies into whichever interpreter you selected:

```bash
python -m unittest discover -s tests -v
```

The current API tests use Python's built-in `unittest`, FastAPI's `TestClient`, and an isolated in-memory SQLite database.

## Deployment version endpoint

- `GET /version`
- On app startup, the application recreates `version.json` (deletes old file if present).
- Metadata is generated automatically: `application_name`, `last_deployment`, `last_code_commit`.
- `last_deployment` is emitted in Indian Standard Time (`UTC+05:30`).
- The endpoint reads `version.json` and returns it as JSON.

## Generalized stock DB model

- SQLAlchemy base/time helpers: `app/db/base.py`
- Stock ORM model: `app/db/models/stock.py`
- Table name: `stock_items`
- Supports generalized item types with `kind` enum: `product`, `ingredient`, `material`, `other`
- Enforces tenant-SKU uniqueness with DB constraint: (`tenant_id`, `sku`)

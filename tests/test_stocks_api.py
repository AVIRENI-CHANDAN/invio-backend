from __future__ import annotations

import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import api_router
from app.db.base import Base
from app.db.session import get_db


class StocksApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.SessionLocal = sessionmaker(
            bind=cls.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    def setUp(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

        app = FastAPI()
        app.include_router(api_router)
        app.dependency_overrides[get_db] = self.override_get_db

        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()

    def override_get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def stock_payload(
        self, *, sku: str = "SKU-1001", name: str = "Notebook"
    ) -> dict[str, object]:
        return {
            "tenant_id": "tenant-1",
            "kind": "product",
            "sku": sku,
            "name": name,
            "barcode": "1234567890123",
            "unit_of_measure": "pcs",
            "status": "active",
            "cost_price": "50.2500",
            "selling_price": "75.5000",
            "currency": "INR",
            "track_inventory": True,
            "reorder_level": "5.0000",
            "reorder_quantity": "10.0000",
            "created_by": "test-user",
        }

    def test_create_stock_with_post(self) -> None:
        response = self.client.post("/stocks", json=self.stock_payload())

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("id", data)
        self.assertEqual(data["tenant_id"], "tenant-1")
        self.assertEqual(data["kind"], "product")
        self.assertEqual(data["sku"], "SKU-1001")
        self.assertEqual(data["name"], "Notebook")
        self.assertEqual(data["status"], "active")

    def test_get_stocks_returns_created_items(self) -> None:
        create_response = self.client.post(
            "/stocks",
            json=self.stock_payload(sku="SKU-2002", name="Coffee Beans"),
        )
        self.assertEqual(create_response.status_code, 201)

        response = self.client.get("/stocks")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["sku"], "SKU-2002")
        self.assertEqual(data[0]["name"], "Coffee Beans")

    def test_product_can_have_ingredient_linkage(self) -> None:
        ingredient_response = self.client.post(
            "/stocks",
            json=self.stock_payload(sku="SKU-ING-1", name="Flour"),
        )
        self.assertEqual(ingredient_response.status_code, 201)
        ingredient_id = ingredient_response.json()["id"]

        product_payload = self.stock_payload(sku="SKU-PROD-1", name="Bread")
        product_payload["kind"] = "product"
        product_payload["components"] = [
            {
                "ingredient_id": ingredient_id,
                "quantity": "2.0000",
            }
        ]

        product_response = self.client.post("/stocks", json=product_payload)
        self.assertEqual(product_response.status_code, 201)
        product_data = product_response.json()
        self.assertEqual(product_data["kind"], "product")
        self.assertEqual(len(product_data.get("components", [])), 1)
        self.assertEqual(product_data["components"][0]["ingredient_id"], ingredient_id)

        can_make_response = self.client.get(f"/stocks/{product_data['id']}/can-make")
        self.assertEqual(can_make_response.status_code, 200)
        self.assertTrue(can_make_response.json()["can_make"])

    def test_can_make_product_fails_when_no_ingredients(self) -> None:
        product_payload = self.stock_payload(sku="SKU-PROD-2", name="Salted Water")
        product_payload["kind"] = "product"

        product_response = self.client.post("/stocks", json=product_payload)
        self.assertEqual(product_response.status_code, 201)
        product_id = product_response.json()["id"]

        can_make_response = self.client.get(f"/stocks/{product_id}/can-make")
        self.assertEqual(can_make_response.status_code, 200)
        self.assertFalse(can_make_response.json()["can_make"])


if __name__ == "__main__":
    unittest.main()

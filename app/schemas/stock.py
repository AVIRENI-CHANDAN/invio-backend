from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import StockKind, StockStatus, UnitOfMeasure


class StockCreate(BaseModel):
    tenant_id: str = Field(..., max_length=64)
    kind: StockKind = StockKind.OTHER
    sku: str = Field(..., max_length=64)
    barcode: str | None = Field(default=None, max_length=64)
    upc: str | None = Field(default=None, max_length=32)
    name: str = Field(..., max_length=255)
    description: str | None = None
    category_id: str | None = Field(default=None, max_length=64)
    category_name: str | None = Field(default=None, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    unit_of_measure: UnitOfMeasure = UnitOfMeasure.PCS
    status: StockStatus = StockStatus.ACTIVE
    cost_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    selling_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    mrp: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    tax_code: str | None = Field(default=None, max_length=50)
    tax_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )
    currency: str = Field(default="INR", min_length=3, max_length=3)
    track_inventory: bool = True
    reorder_level: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    reorder_quantity: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    max_stock_level: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    default_location_id: str | None = Field(default=None, max_length=64)
    expiry_tracking_enabled: bool = False
    batch_tracking_enabled: bool = False
    serial_tracking_enabled: bool = False
    created_by: str | None = Field(default=None, max_length=128)
    updated_by: str | None = Field(default=None, max_length=128)


class StockUpdate(BaseModel):
    tenant_id: str | None = Field(default=None, max_length=64)
    kind: StockKind | None = None
    sku: str | None = Field(default=None, max_length=64)
    barcode: str | None = Field(default=None, max_length=64)
    upc: str | None = Field(default=None, max_length=32)
    name: str | None = Field(default=None, max_length=255)
    description: str | None = None
    category_id: str | None = Field(default=None, max_length=64)
    category_name: str | None = Field(default=None, max_length=255)
    brand: str | None = Field(default=None, max_length=255)
    unit_of_measure: UnitOfMeasure | None = None
    status: StockStatus | None = None
    cost_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    selling_price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    mrp: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    tax_code: str | None = Field(default=None, max_length=50)
    tax_rate: Decimal | None = Field(
        default=None,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
    )
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    track_inventory: bool | None = None
    reorder_level: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    reorder_quantity: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    max_stock_level: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=18,
        decimal_places=4,
    )
    default_location_id: str | None = Field(default=None, max_length=64)
    expiry_tracking_enabled: bool | None = None
    batch_tracking_enabled: bool | None = None
    serial_tracking_enabled: bool | None = None
    updated_by: str | None = Field(default=None, max_length=128)


class StockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: str
    kind: StockKind
    sku: str
    barcode: str | None
    upc: str | None
    name: str
    description: str | None
    category_id: str | None
    category_name: str | None
    brand: str | None
    unit_of_measure: UnitOfMeasure
    status: StockStatus
    cost_price: Decimal | None
    selling_price: Decimal | None
    mrp: Decimal | None
    tax_code: str | None
    tax_rate: Decimal | None
    currency: str
    track_inventory: bool
    reorder_level: Decimal
    reorder_quantity: Decimal
    max_stock_level: Decimal | None
    default_location_id: str | None
    expiry_tracking_enabled: bool
    batch_tracking_enabled: bool
    serial_tracking_enabled: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None

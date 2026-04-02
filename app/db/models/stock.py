from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, ist_now


class StockKind(str, enum.Enum):
    PRODUCT = "product"
    INGREDIENT = "ingredient"
    MATERIAL = "material"
    OTHER = "other"


class StockStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class UnitOfMeasure(str, enum.Enum):
    PCS = "pcs"
    KG = "kg"
    LITER = "liter"


class StockItem(Base):
    """
    Generalized stock catalog model that can represent products, ingredients, or raw materials.
    """

    __tablename__ = "stock_items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_stock_items_tenant_sku"),
        Index("ix_stock_items_tenant_id", "tenant_id"),
        Index("ix_stock_items_status", "status"),
        Index("ix_stock_items_barcode", "barcode"),
        CheckConstraint(
            "cost_price IS NULL OR cost_price >= 0",
            name="ck_stock_items_cost_price_non_negative",
        ),
        CheckConstraint(
            "selling_price IS NULL OR selling_price >= 0",
            name="ck_stock_items_selling_price_non_negative",
        ),
        CheckConstraint(
            "mrp IS NULL OR mrp >= 0",
            name="ck_stock_items_mrp_non_negative",
        ),
        CheckConstraint(
            "tax_rate IS NULL OR (tax_rate >= 0 AND tax_rate <= 100)",
            name="ck_stock_items_tax_rate_range",
        ),
        CheckConstraint(
            "reorder_level >= 0",
            name="ck_stock_items_reorder_level_non_negative",
        ),
        CheckConstraint(
            "reorder_quantity >= 0",
            name="ck_stock_items_reorder_quantity_non_negative",
        ),
        CheckConstraint(
            "max_stock_level IS NULL OR max_stock_level >= 0",
            name="ck_stock_items_max_stock_level_non_negative",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="Owning tenant/org identifier. Kept as string to support UUID or integer external IDs.",
    )
    kind: Mapped[StockKind] = mapped_column(
        Enum(StockKind, name="stock_kind"),
        nullable=False,
        default=StockKind.OTHER,
    )
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    upc: Mapped[str | None] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    category_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unit_of_measure: Mapped[UnitOfMeasure] = mapped_column(
        Enum(UnitOfMeasure, name="unit_of_measure"),
        nullable=False,
        default=UnitOfMeasure.PCS,
    )
    status: Mapped[StockStatus] = mapped_column(
        Enum(StockStatus, name="stock_status"),
        nullable=False,
        default=StockStatus.ACTIVE,
    )

    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    selling_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    tax_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tax_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")

    track_inventory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    reorder_level: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    reorder_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4),
        nullable=False,
        default=Decimal("0"),
    )
    max_stock_level: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 4), nullable=True
    )
    default_location_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    expiry_tracking_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    batch_tracking_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    serial_tracking_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    components: Mapped[list["StockItemComponent"]] = relationship(
        "StockItemComponent",
        back_populates="parent",
        foreign_keys="[StockItemComponent.parent_id]",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    used_as_component: Mapped[list["StockItemComponent"]] = relationship(
        "StockItemComponent",
        back_populates="ingredient",
        foreign_keys="[StockItemComponent.ingredient_id]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=ist_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=ist_now,
        onupdate=ist_now,
    )
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(String(128), nullable=True)


class StockItemComponent(Base):
    __tablename__ = "stock_item_components"
    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "ingredient_id",
            name="uq_stock_item_components_parent_ingredient",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("stock_items.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("stock_items.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=Decimal("1")
    )

    parent: Mapped[StockItem] = relationship(
        "StockItem",
        back_populates="components",
        foreign_keys=[parent_id],
    )
    ingredient: Mapped[StockItem] = relationship(
        "StockItem",
        back_populates="used_as_component",
        foreign_keys=[ingredient_id],
    )

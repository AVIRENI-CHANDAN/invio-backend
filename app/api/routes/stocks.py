from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import StockItem, StockItemComponent, StockKind, StockStatus
from app.db.session import get_db
from app.schemas.stock import StockCreate, StockRead, StockUpdate

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"],
)


def _get_stock_or_404(db: Session, stock_id: uuid.UUID) -> StockItem:
    stock = db.get(StockItem, stock_id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock item not found")
    return stock


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A stock item with this tenant_id and sku already exists",
        ) from exc


@router.post("", response_model=StockRead, status_code=status.HTTP_201_CREATED)
def create_stock(
    payload: StockCreate,
    db: Session = Depends(get_db),
) -> StockItem:
    payload_data = payload.model_dump(exclude={"components"})
    components_data = payload.model_dump().get("components", [])

    stock = StockItem(**payload_data)
    for component in components_data:
        ingredient = db.get(StockItem, component["ingredient_id"])
        if ingredient is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredient stock item '{component['ingredient_id']}' not found",
            )
        stock.components.append(
            StockItemComponent(
                ingredient_id=component["ingredient_id"],
                quantity=component["quantity"],
            )
        )

    db.add(stock)
    _commit_or_raise_conflict(db)
    db.refresh(stock)
    return stock


@router.get("", response_model=list[StockRead])
def list_stocks(
    tenant_id: str | None = Query(default=None, max_length=64),
    kind: StockKind | None = Query(default=None),
    status_filter: StockStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[StockItem]:
    stmt = select(StockItem).order_by(StockItem.created_at.desc())

    if tenant_id is not None:
        stmt = stmt.where(StockItem.tenant_id == tenant_id)
    if kind is not None:
        stmt = stmt.where(StockItem.kind == kind)
    if status_filter is not None:
        stmt = stmt.where(StockItem.status == status_filter)

    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.get("/{stock_id}", response_model=StockRead)
def get_stock(
    stock_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> StockItem:
    return _get_stock_or_404(db, stock_id)


@router.get("/{stock_id}/can-make")
def can_make_stock(
    stock_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    stock = _get_stock_or_404(db, stock_id)

    if stock.kind != StockKind.PRODUCT:
        return {
            "can_make": True,
            "reason": "Not a product item, no ingredient recipe required",
        }

    if not stock.components:
        return {
            "can_make": False,
            "reason": "No ingredient linkage configured for this product",
        }

    missing_ingredients = [
        comp.ingredient_id for comp in stock.components if comp.ingredient is None
    ]
    if missing_ingredients:
        return {
            "can_make": False,
            "reason": "One or more linked ingredients do not exist",
            "missing_ingredient_ids": missing_ingredients,
        }

    return {
        "can_make": True,
        "component_count": len(stock.components),
        "details": [
            {
                "ingredient_id": comp.ingredient_id,
                "ingredient_name": comp.ingredient.name,
                "quantity": str(comp.quantity),
            }
            for comp in stock.components
        ],
    }


@router.patch("/{stock_id}", response_model=StockRead)
def update_stock(
    stock_id: uuid.UUID,
    payload: StockUpdate,
    db: Session = Depends(get_db),
) -> StockItem:
    stock = _get_stock_or_404(db, stock_id)
    payload_data = payload.model_dump(exclude_unset=True)

    components_data = payload_data.pop("components", None)
    for field, value in payload_data.items():
        setattr(stock, field, value)

    if components_data is not None:
        stock.components.clear()
        for component in components_data:
            ingredient = db.get(StockItem, component["ingredient_id"])
            if ingredient is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingredient stock item '{component['ingredient_id']}' not found",
                )
            stock.components.append(
                StockItemComponent(
                    ingredient_id=component["ingredient_id"],
                    quantity=component["quantity"],
                )
            )

    _commit_or_raise_conflict(db)
    db.refresh(stock)
    return stock


@router.delete("/{stock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stock(
    stock_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Response:
    stock = _get_stock_or_404(db, stock_id)
    db.delete(stock)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

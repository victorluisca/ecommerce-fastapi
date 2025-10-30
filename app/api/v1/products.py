from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.dependencies import require_admin
from app.database import get_session
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

router = APIRouter()


@router.get("/", response_model=list[ProductResponse])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
):
    products = session.exec(select(Product).offset(skip).limit(limit)).all()

    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock_quantity=product_data.stock_quantity,
        image_url=product_data.image_url,
    )

    session.add(new_product)
    session.commit()
    session.refresh(new_product)

    return new_product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    update_data = product_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)

    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    session.delete(product)
    session.commit()

    return None

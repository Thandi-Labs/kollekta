from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.payment import B2CTransaction, C2BTransaction, STKTransaction
from src.schemas.payment import B2CTransactionOut, C2BTransactionOut, PaginatedResponse, STKTransactionOut

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/stk", response_model=PaginatedResponse, summary="List STK push transactions")
def list_stk(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(STKTransaction)
    if status:
        query = query.filter(STKTransaction.status == status)
    total = query.count()
    items = query.order_by(STKTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[STKTransactionOut.model_validate(t) for t in items],
    )


@router.get("/stk/{checkout_request_id}", response_model=STKTransactionOut, summary="Get a single STK transaction")
def get_stk(checkout_request_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    transaction = db.query(STKTransaction).filter_by(checkout_request_id=checkout_request_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return STKTransactionOut.model_validate(transaction)


@router.get("/c2b", response_model=PaginatedResponse, summary="List C2B transactions")
def list_c2b(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(C2BTransaction)
    total = query.count()
    items = query.order_by(C2BTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[C2BTransactionOut.model_validate(t) for t in items],
    )


@router.get("/b2c", response_model=PaginatedResponse, summary="List B2C disbursements")
def list_b2c(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(B2CTransaction)
    if status:
        query = query.filter(B2CTransaction.status == status)
    total = query.count()
    items = query.order_by(B2CTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[B2CTransactionOut.model_validate(t) for t in items],
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.payment import C2BTransaction
from src.schemas.mpesa import C2BConfirmationPayload
from src.services import daraja

router = APIRouter(prefix="/c2b", tags=["C2B"])


@router.post("/register", summary="Register C2B validation and confirmation URLs with Daraja")
def register():
    result = daraja.register_c2b_urls()
    return result


@router.post("/validation", summary="Daraja C2B validation callback", include_in_schema=False)
def validation():
    # Accept all transactions; implement business rules here if needed
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.post("/confirmation", summary="Daraja C2B confirmation callback", include_in_schema=False)
def confirmation(payload: C2BConfirmationPayload, db: Session = Depends(get_db)):
    existing = db.query(C2BTransaction).filter_by(trans_id=payload.TransID).first()
    if existing:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    transaction = C2BTransaction(
        transaction_type=payload.TransactionType,
        trans_id=payload.TransID,
        trans_time=payload.TransTime,
        trans_amount=int(float(payload.TransAmount)),
        business_shortcode=payload.BusinessShortCode,
        bill_ref_number=payload.BillRefNumber,
        invoice_number=payload.InvoiceNumber,
        org_account_balance=payload.OrgAccountBalance,
        third_party_trans_id=payload.ThirdPartyTransID,
        msisdn=payload.MSISDN,
        first_name=payload.FirstName,
        middle_name=payload.MiddleName,
        last_name=payload.LastName,
    )
    db.add(transaction)
    db.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}

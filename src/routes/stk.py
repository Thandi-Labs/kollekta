from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.payment import STKTransaction
from src.schemas.mpesa import STKCallbackPayload, STKPushRequest
from src.services import daraja

router = APIRouter(prefix="/stk", tags=["STK Push"])


@router.post("/push", summary="Initiate STK push to customer's phone")
def push(request: STKPushRequest, db: Session = Depends(get_db)):
    result = daraja.initiate_stk_push(
        phone=request.phone_number,
        amount=request.amount,
        account_reference=request.account_reference,
        transaction_desc=request.transaction_desc or "Payment",
    )

    if result.get("ResponseCode") != "0":
        raise HTTPException(status_code=400, detail=result.get("ResponseDescription", "STK push failed"))

    transaction = STKTransaction(
        merchant_request_id=result["MerchantRequestID"],
        checkout_request_id=result["CheckoutRequestID"],
        phone_number=request.phone_number,
        amount=request.amount,
        account_reference=request.account_reference,
        transaction_desc=request.transaction_desc,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "checkout_request_id": transaction.checkout_request_id,
        "status": "pending",
        "message": result.get("CustomerMessage", "Request accepted for processing"),
    }


@router.post("/callback", summary="Daraja STK push result callback", include_in_schema=False)
def callback(payload: STKCallbackPayload, db: Session = Depends(get_db)):
    body = payload.Body.stkCallback
    transaction = db.query(STKTransaction).filter_by(
        checkout_request_id=body.CheckoutRequestID
    ).first()

    if not transaction:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    transaction.result_code = str(body.ResultCode)
    transaction.result_desc = body.ResultDesc

    if body.ResultCode == 0 and body.CallbackMetadata:
        items = {item.Name: item.Value for item in body.CallbackMetadata.Item}
        transaction.mpesa_receipt_number = str(items.get("MpesaReceiptNumber", ""))
        transaction.status = "success"
    else:
        transaction.status = "failed"

    db.commit()
    return {"ResultCode": 0, "ResultDesc": "Accepted"}

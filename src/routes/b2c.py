from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.payment import B2CTransaction
from src.schemas.mpesa import B2CRequest, B2CResultPayload, B2CTimeoutPayload
from src.services import daraja

router = APIRouter(prefix="/b2c", tags=["B2C"])


@router.post("/disburse", summary="Initiate B2C disbursement to a phone number")
def disburse(request: B2CRequest, db: Session = Depends(get_db)):
    result = daraja.initiate_b2c(
        phone=request.receiver_phone,
        amount=request.amount,
        command_id=request.command_id,
        remarks=request.remarks or "Disbursement",
    )

    if result.get("ResponseCode") != "0":
        raise HTTPException(status_code=400, detail=result.get("ResponseDescription", "B2C request failed"))

    transaction = B2CTransaction(
        conversation_id=result.get("ConversationID"),
        originator_conversation_id=result["OriginatorConversationID"],
        receiver_phone=request.receiver_phone,
        amount=request.amount,
        command_id=request.command_id,
        remarks=request.remarks,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "originator_conversation_id": transaction.originator_conversation_id,
        "status": "pending",
        "message": result.get("ResponseDescription", "Request accepted for processing"),
    }


@router.post("/result", summary="Daraja B2C result callback", include_in_schema=False)
def result(payload: B2CResultPayload, db: Session = Depends(get_db)):
    body = payload.Result
    transaction = db.query(B2CTransaction).filter_by(
        originator_conversation_id=body.OriginatorConversationID
    ).first()

    if not transaction:
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    transaction.result_code = str(body.ResultCode)
    transaction.result_desc = body.ResultDesc

    if body.ResultCode == 0 and body.ResultParameters:
        params = body.ResultParameters.ResultParameter
        if not isinstance(params, list):
            params = [params]
        items = {p.Key: p.Value for p in params}
        transaction.transaction_receipt = str(items.get("TransactionReceipt", ""))
        transaction.receiver_party_public_name = str(items.get("ReceiverPartyPublicName", ""))
        transaction.status = "completed"
    else:
        transaction.status = "failed"

    db.commit()
    return {"ResultCode": 0, "ResultDesc": "Accepted"}


@router.post("/timeout", summary="Daraja B2C timeout callback", include_in_schema=False)
def timeout(payload: B2CTimeoutPayload, db: Session = Depends(get_db)):
    body = payload.Result
    transaction = db.query(B2CTransaction).filter_by(
        originator_conversation_id=body.OriginatorConversationID
    ).first()

    if transaction:
        transaction.status = "failed"
        transaction.result_code = str(body.ResultCode)
        transaction.result_desc = body.ResultDesc
        db.commit()

    return {"ResultCode": 0, "ResultDesc": "Accepted"}

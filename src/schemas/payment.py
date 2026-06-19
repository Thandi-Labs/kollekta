from datetime import datetime
from pydantic import BaseModel


class STKTransactionOut(BaseModel):
    id: str
    checkout_request_id: str
    phone_number: str
    amount: int
    account_reference: str
    transaction_desc: str | None
    status: str
    mpesa_receipt_number: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class C2BTransactionOut(BaseModel):
    id: str
    trans_id: str
    trans_time: str
    trans_amount: int
    business_shortcode: str
    bill_ref_number: str
    msisdn: str
    first_name: str | None
    last_name: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class B2CTransactionOut(BaseModel):
    id: str
    originator_conversation_id: str
    receiver_phone: str
    amount: int
    command_id: str
    remarks: str | None
    status: str
    transaction_receipt: str | None
    receiver_party_public_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list

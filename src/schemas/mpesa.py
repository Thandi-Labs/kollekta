from typing import Any
from pydantic import BaseModel, field_validator


class STKPushRequest(BaseModel):
    phone_number: str
    amount: int
    account_reference: str
    transaction_desc: str | None = None

    @field_validator("phone_number")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        v = v.strip().replace("+", "").replace(" ", "")
        if v.startswith("0"):
            v = "254" + v[1:]
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


# --- STK Callback ---

class STKCallbackItem(BaseModel):
    Name: str
    Value: Any = None


class STKCallbackMetadata(BaseModel):
    Item: list[STKCallbackItem] = []


class STKCallbackBody(BaseModel):
    MerchantRequestID: str
    CheckoutRequestID: str
    ResultCode: int
    ResultDesc: str
    CallbackMetadata: STKCallbackMetadata | None = None


class STKCallbackWrapper(BaseModel):
    stkCallback: STKCallbackBody


class STKCallbackPayload(BaseModel):
    Body: STKCallbackWrapper


# --- C2B Confirmation ---

class C2BConfirmationPayload(BaseModel):
    TransactionType: str
    TransID: str
    TransTime: str
    TransAmount: str
    BusinessShortCode: str
    BillRefNumber: str
    InvoiceNumber: str | None = None
    OrgAccountBalance: str | None = None
    ThirdPartyTransID: str | None = None
    MSISDN: str
    FirstName: str | None = None
    MiddleName: str | None = None
    LastName: str | None = None


# --- B2C Request ---

class B2CCommandID(str):
    SALARY = "SalaryPayment"
    BUSINESS = "BusinessPayment"
    PROMOTION = "PromotionPayment"


class B2CRequest(BaseModel):
    receiver_phone: str
    amount: int
    command_id: str = "BusinessPayment"
    remarks: str | None = None

    @field_validator("receiver_phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        v = v.strip().replace("+", "").replace(" ", "")
        if v.startswith("0"):
            v = "254" + v[1:]
        return v

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

    @field_validator("command_id")
    @classmethod
    def valid_command_id(cls, v: str) -> str:
        allowed = {"SalaryPayment", "BusinessPayment", "PromotionPayment"}
        if v not in allowed:
            raise ValueError(f"command_id must be one of {allowed}")
        return v


# --- B2C Result ---

class B2CResultParameter(BaseModel):
    Key: str
    Value: Any = None


class B2CResultParameters(BaseModel):
    ResultParameter: list[B2CResultParameter] | B2CResultParameter


class B2CResultBody(BaseModel):
    ResultType: int
    ResultCode: int
    ResultDesc: str
    OriginatorConversationID: str
    ConversationID: str
    TransactionID: str | None = None
    ResultParameters: B2CResultParameters | None = None


class B2CResultPayload(BaseModel):
    Result: B2CResultBody


class B2CTimeoutPayload(BaseModel):
    Result: B2CResultBody

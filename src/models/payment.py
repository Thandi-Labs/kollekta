import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class STKTransaction(Base):
    __tablename__ = "stk_transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    merchant_request_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    checkout_request_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(Integer)
    account_reference: Mapped[str] = mapped_column(String(50))
    transaction_desc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    mpesa_receipt_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    result_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    result_desc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())


class C2BTransaction(Base):
    __tablename__ = "c2b_transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_type: Mapped[str] = mapped_column(String(50))
    trans_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    trans_time: Mapped[str] = mapped_column(String(20))
    trans_amount: Mapped[int] = mapped_column(Integer)
    business_shortcode: Mapped[str] = mapped_column(String(20))
    bill_ref_number: Mapped[str] = mapped_column(String(100))
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    org_account_balance: Mapped[str | None] = mapped_column(String(50), nullable=True)
    third_party_trans_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    msisdn: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class B2CTransaction(Base):
    __tablename__ = "b2c_transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True, index=True)
    originator_conversation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    receiver_phone: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(Integer)
    command_id: Mapped[str] = mapped_column(String(50))
    remarks: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    result_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    result_desc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    transaction_receipt: Mapped[str | None] = mapped_column(String(50), nullable=True)
    receiver_party_public_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

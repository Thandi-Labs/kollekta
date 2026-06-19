import base64
from datetime import datetime

import httpx

from src.config import settings


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S")


def _stk_password(timestamp: str) -> str:
    raw = f"{settings.mpesa_shortcode}{settings.mpesa_passkey}{timestamp}"
    return base64.b64encode(raw.encode()).decode()


def _security_credential() -> str:
    # Sandbox: base64-encode the initiator password directly.
    # Production: encrypt with Safaricom's public certificate before encoding.
    return base64.b64encode(settings.mpesa_b2c_initiator_password.encode()).decode()


def _auth_header() -> dict:
    credentials = base64.b64encode(
        f"{settings.mpesa_consumer_key}:{settings.mpesa_consumer_secret}".encode()
    ).decode()
    return {"Authorization": f"Basic {credentials}"}


def get_access_token() -> str:
    url = f"{settings.mpesa_base_url}/oauth/v1/generate?grant_type=client_credentials"
    response = httpx.get(url, headers=_auth_header())
    response.raise_for_status()
    return response.json()["access_token"]


def _bearer_header() -> dict:
    return {"Authorization": f"Bearer {get_access_token()}"}


def initiate_stk_push(phone: str, amount: int, account_reference: str, transaction_desc: str) -> dict:
    ts = _timestamp()
    payload = {
        "BusinessShortCode": settings.mpesa_shortcode,
        "Password": _stk_password(ts),
        "Timestamp": ts,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.mpesa_shortcode,
        "PhoneNumber": phone,
        "CallBackURL": f"{settings.mpesa_callback_base_url}/api/v1/stk/callback",
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc or "Payment",
    }
    response = httpx.post(
        f"{settings.mpesa_base_url}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=_bearer_header(),
    )
    response.raise_for_status()
    return response.json()


def register_c2b_urls() -> dict:
    payload = {
        "ShortCode": settings.mpesa_shortcode,
        "ResponseType": "Completed",
        "ConfirmationURL": f"{settings.mpesa_callback_base_url}/api/v1/c2b/confirmation",
        "ValidationURL": f"{settings.mpesa_callback_base_url}/api/v1/c2b/validation",
    }
    response = httpx.post(
        f"{settings.mpesa_base_url}/mpesa/c2b/v1/registerurl",
        json=payload,
        headers=_bearer_header(),
    )
    response.raise_for_status()
    return response.json()


def initiate_b2c(phone: str, amount: int, command_id: str, remarks: str) -> dict:
    payload = {
        "InitiatorName": settings.mpesa_b2c_initiator_name,
        "SecurityCredential": _security_credential(),
        "CommandID": command_id,
        "Amount": amount,
        "PartyA": settings.mpesa_shortcode,
        "PartyB": phone,
        "Remarks": remarks or "Disbursement",
        "QueueTimeOutURL": f"{settings.mpesa_callback_base_url}/api/v1/b2c/timeout",
        "ResultURL": f"{settings.mpesa_callback_base_url}/api/v1/b2c/result",
        "Occasion": "",
    }
    response = httpx.post(
        f"{settings.mpesa_base_url}/mpesa/b2c/v1/paymentrequest",
        json=payload,
        headers=_bearer_header(),
    )
    response.raise_for_status()
    return response.json()

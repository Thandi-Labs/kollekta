import fastapi

from src.routes import b2c, c2b, payments, stk

app = fastapi.FastAPI(
    title="Kollekta",
    description="M-Pesa Daraja payment collection and disbursement microservice",
    version="1.0.0",
)

app.include_router(stk.router, prefix="/api/v1")
app.include_router(c2b.router, prefix="/api/v1")
app.include_router(b2c.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}

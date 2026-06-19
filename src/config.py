from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    mpesa_environment: str = "sandbox"
    mpesa_consumer_key: str
    mpesa_consumer_secret: str
    mpesa_shortcode: str
    mpesa_passkey: str
    mpesa_b2c_initiator_name: str
    mpesa_b2c_initiator_password: str
    mpesa_callback_base_url: str

    @property
    def mpesa_base_url(self) -> str:
        if self.mpesa_environment == "production":
            return "https://api.safaricom.co.ke"
        return "https://sandbox.safaricom.co.ke"

    model_config = {"env_file": ".env"}


settings = Settings()

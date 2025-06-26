# settings.py
import os
from dotenv import load_dotenv

load_dotenv()                      # .env in den Prozess laden

class BaseConfig:
    """Gemeinsame Konfiguration (alle Umgebungen)"""

    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

    # Google Analytics
    GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "")

    # reCAPTCHA v2
    RECAPTCHA_SITE_KEY   = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_ENABLED    = os.getenv("RECAPTCHA_ENABLED", "false").lower() in ("true", "1", "yes")

    # Mail
    MAIL_SERVER   = os.getenv("MAIL_SERVER")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 0))
    MAIL_USE_TLS  = os.getenv("MAIL_USE_TLS",  "false").lower() in ("true", "1", "yes")
    MAIL_USE_SSL  = os.getenv("MAIL_USE_SSL",  "false").lower() in ("true", "1", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    # Sonstiges
    PDF_PATH = os.getenv("PDF_PATH")

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV   = "development"

class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV   = "production"

# Mapping für create_app()
config = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}

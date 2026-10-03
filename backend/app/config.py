import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "shopping-cart-secret-key-2026")

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        import tempfile
        tmp_db = os.path.join(tempfile.gettempdir(), "shopping_cart.db")
        db_url = f"sqlite:///{tmp_db}"

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False



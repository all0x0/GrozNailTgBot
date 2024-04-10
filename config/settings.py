import os

TOKEN = os.environ.get("TOKEN", "6898513530:AAFswy2dAPpnNSuVfr1Zm3MA7XcjHktIc68")
URL = os.environ.get("URL", "https://8159-88-241-48-94.ngrok-free.app")
WEBHOOK_PATH = f"/bot/{TOKEN.split(':')[1]}"
WEBHOOK_URL = f"{URL}{WEBHOOK_PATH}"

POSTGRES_HOST = os.environ.get("VERCEL_POSTGRES_HOST", "localhost")
POSTGRES_USER = os.environ.get("VERCEL_POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("VERCEL_POSTGRES_PASSWORD", "123")
POSTGRES_PORT = os.environ.get("VERCEL_POSTGRES_PORT", "5432")
POSTGRES_DATABASE = os.environ.get("VERCEL_POSTGRES_DATABASE", "postgres")
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"

PRICE_URL = os.environ.get("PRICE_URL", "https://i.imgur.com/r3WlE1J.png")
ADDRESS_PHOTO_URL = os.environ.get(
    "ADDRESS_PHOTO_URL", "https://i.imgur.com/Zw2HanM.png"
)
ADDRESS_URL = os.environ.get("ADDRESS_URL", "a link on google maps")

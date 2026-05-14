import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ.get('DB_NAME', 'aic_kapsowar')

client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Collection accessors
def coll(name: str):
    return db[name]

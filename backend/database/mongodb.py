from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.models.prediction import Prediction
from backend.models.trend import Trend
from backend.models.opportunity import Opportunity

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "tendancy_analysis"

client = AsyncIOMotorClient(MONGO_URI)

async def init_db():
    await init_beanie(
        database=client[DB_NAME],
        document_models=[Prediction, Trend, Opportunity],
    )
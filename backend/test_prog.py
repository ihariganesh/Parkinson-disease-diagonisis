import asyncio
from app.db.database import SessionLocal
from app.services.progression_engine import ProgressionEngine

db = SessionLocal()
engine = ProgressionEngine(db)
res = engine.get_progression_metrics("some_id") # using random ID so it should just return empty
print(res)

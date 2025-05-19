from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from app.routes import auth, departments

app = FastAPI(title="Revival House Global API",
              description="Church Management System API",
              version="1.0.0")

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.mongodb_url)
    app.mongodb = app.mongodb_client[settings.database_name]
    # Attach db to routers
    auth.router.db = app.mongodb
    departments.router.db = app.mongodb

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(departments.router, prefix="/departments", tags=["departments"])
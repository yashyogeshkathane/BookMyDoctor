from typing import Any

from app.config.settings import settings
from pymongo import ASCENDING

try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
except ModuleNotFoundError:
    AsyncIOMotorClient = None
    AsyncIOMotorDatabase = Any

mongodb_client: Any = None
database: Any = None
DEFAULT_COLLECTIONS = [
    "users",
    "doctors",
    "appointments",
]


async def connect_to_mongo() -> Any:
    global mongodb_client, database

    if AsyncIOMotorClient is not None:
        mongodb_client = AsyncIOMotorClient(settings.mongodb_uri)
        await mongodb_client.admin.command("ping")
        database = mongodb_client[settings.mongodb_db_name]
        return database

    if MongoClient is not None:
        mongodb_client = MongoClient(settings.mongodb_uri)
        mongodb_client.admin.command("ping")
        database = mongodb_client[settings.mongodb_db_name]
        return database

    raise RuntimeError(
        "MongoDB client dependency is missing. Install either 'motor' or 'pymongo'."
    )


async def initialize_database() -> None:
    db = get_database()

    if AsyncIOMotorClient is not None and hasattr(db, "list_collection_names"):
        existing_collections = await db.list_collection_names()
        for collection_name in DEFAULT_COLLECTIONS:
            if collection_name not in existing_collections:
                await db.create_collection(collection_name)
        await db["appointments"].create_index(
            [("doctor_id", ASCENDING), ("date_key", ASCENDING), ("start_time", ASCENDING)],
            unique=True,
            partialFilterExpression={"status": "confirmed"},
            name="uniq_confirmed_slot_per_doctor",
        )
        return

    existing_collections = db.list_collection_names()
    for collection_name in DEFAULT_COLLECTIONS:
        if collection_name not in existing_collections:
            db.create_collection(collection_name)
    db["appointments"].create_index(
        [("doctor_id", ASCENDING), ("date_key", ASCENDING), ("start_time", ASCENDING)],
        unique=True,
        partialFilterExpression={"status": "confirmed"},
        name="uniq_confirmed_slot_per_doctor",
    )


async def close_mongo_connection() -> None:
    global mongodb_client, database

    if mongodb_client is not None:
        mongodb_client.close()
        mongodb_client = None
        database = None


def get_database() -> Any:
    if database is None:
        raise RuntimeError("Database is not initialized. Start the application first.")
    return database

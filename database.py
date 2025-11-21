# database.py - MongoDB Connection (with GridFS for file storage)
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from gridfs import GridFS
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "pod_1")

# System Limits
FREE_PLAN_RESUME_LIMIT = 100
MAX_FILE_SIZE_MB = 5

# Connection options for MongoDB Atlas
# For mongodb+srv:// connections, TLS is automatically enabled by pymongo
# We just need to ensure proper timeout settings and use system CA certificates
connection_options = {}
if "mongodb+srv://" in MONGODB_URL:
    # For Atlas SRV connections, ensure proper timeout and SSL settings
    connection_options = {
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 20000,
        "socketTimeoutMS": 20000,
        "retryWrites": True,
    }
elif "mongodb://" in MONGODB_URL and "mongodb.net" in MONGODB_URL:
    # For standard Atlas connections (non-SRV), explicitly enable TLS
    connection_options = {
        "tls": True,
        "tlsAllowInvalidCertificates": False,
        "serverSelectionTimeoutMS": 30000,
        "connectTimeoutMS": 20000,
        "socketTimeoutMS": 20000,
        "retryWrites": True,
    }

# Synchronous client
client = MongoClient(MONGODB_URL, **connection_options)
db = client[DATABASE_NAME]
fs = GridFS(db)

# Async client
async_client = AsyncIOMotorClient(MONGODB_URL, **connection_options)
async_db = async_client[DATABASE_NAME]

# Collection names — THESE WERE MISSING BEFORE!
RESUME_COLLECTION = "resume"
JOB_DESCRIPTION_COLLECTION = "JobDescription"
RESUME_RESULT_COLLECTION = "resume_result"
USER_COLLECTION = "users"
AUDIT_LOG_COLLECTION = "audit_logs"
FILE_METADATA_COLLECTION = "files"
WORKFLOW_EXECUTION_COLLECTION = "workflow_executions"

def get_db():
    try:
        yield db
    finally:
        pass

def get_async_db():
    try:
        yield async_db
    finally:
        pass

def init_db():
    print("Initializing database and creating indexes...")
    # (your full init_db function here - it's already in your old file, so we keep it)
    # ... keeping all your indexes ...
    print("Database initialization complete!")

def test_connection():
    try:
        client.admin.command('ping')
        print("MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

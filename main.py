# main.py - FastAPI Application Entry Point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Import database initialization
from database import init_db, test_connection

# Import routers
from routers import auth, resumes, job_descriptions, matching, files, analytics, audit, workflow

# Note: Using MongoDB GridFS for file storage (no Azure needed!)
# Free plan: 10 resumes max, 5MB per file = 50MB total storage

load_dotenv()


def get_cors_settings():
    """Return (origins, allow_credentials) derived from env configuration."""
    raw_origins = os.getenv("CORS_ORIGINS", "")
    cors_list = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    if cors_list:
        return cors_list, True
    return ["*"], False


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting HR Resume Comparator API...")
    if test_connection():
        init_db()
    else:
        print("⚠️ Database connection failed! Please check your MongoDB connection.")
    
    yield
    
    # Shutdown
    print("👋 Shutting down HR Resume Comparator API...")

# Initialize FastAPI app
app = FastAPI(
    title="HR Resume Comparator API",
    description="AgenticAI-powered resume matching system for HR recruitment",
    version="1.0.0",
    lifespan=lifespan
)
# ============================================
# Prometheus Metrics Instrumentation
# ============================================
from prometheus_fastapi_instrumentator import Instrumentator

# Initialize Prometheus instrumentator
# This automatically tracks:
# - http_requests_total (total requests by method, path, status)
# - http_request_duration_seconds (request latency histogram)
# - http_requests_in_progress (currently processing requests)
instrumentator = Instrumentator(
    should_group_status_codes=False,      # Keep individual status codes (200, 201, 404, 500)
    should_ignore_untemplated=True,       # Ignore paths without URL templates
    should_respect_env_var=True,          # Can disable via ENABLE_METRICS=false
    excluded_handlers=["/health", "/metrics"],  # Don't track these endpoints
)

# Instrument the app and expose /metrics endpoint
instrumentator.instrument(app).expose(app, endpoint="/metrics")
# ============================================

# CORS Configuration
cors_origins, allow_credentials = get_cors_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(job_descriptions.router)
app.include_router(matching.router)
app.include_router(files.router)
app.include_router(analytics.router)
app.include_router(audit.router)
app.include_router(workflow.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to HR Resume Comparator API",
        "version": "1.0.0",
        "description": "AgenticAI-powered resume matching system",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "service": "HR Resume Comparator API"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/info")
def api_info():
    """API information"""
    return {
        "api_name": "HR Resume Comparator",
        "version": "1.0.0",
        "database": "MongoDB",
        "collections": [
            "resume",
            "JobDescription",
            "resume_result",
            "users",
            "audit_logs",
            "files"
        ],
        "features": [
            "Resume Upload & Parsing",
            "Job Description Management",
            "AI-Powered Matching",
            "Multi-Platform Resume Fetching",
            "Analytics & Reporting",
            "User Authentication & Authorization"
        ],
        "endpoints": {
            "auth": "/auth",
            "resumes": "/resumes",
            "job_descriptions": "/job-descriptions",
            "matching": "/matching",
            "files": "/files",
            "analytics": "/analytics"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


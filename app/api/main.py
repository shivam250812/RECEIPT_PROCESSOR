"""
Main FastAPI application for the OCR Receipt Processor API.
Configures routes, middleware, and application settings.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ..core.config import settings
from ..core.database import init_db, create_indexes, check_db_connection
from .routes import upload, search, analytics, export, receipts

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Include routers
app.include_router(upload.router)
app.include_router(receipts.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(export.router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    print("🚀 Starting OCR Receipt Processor API...")
    
    # Initialize database
    try:
        init_db()
        create_indexes()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise
    
    # Check database connection
    if not check_db_connection():
        print("❌ Database connection failed")
        raise Exception("Database connection failed")
    
    print("✅ API startup completed")

@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "OCR Receipt Processor API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    db_healthy = check_db_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.API_VERSION
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    ) 
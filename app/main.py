"""
Main Application Entry Point

This is where the FastAPI application is created and configured.
This file:
1. Creates the FastAPI app instance
2. Configures middleware (CORS, error handling)
3. Includes all routers
4. Defines root/health endpoints

To run the application:
    uvicorn app.main:app --reload

The "--reload" flag enables auto-restart on code changes (dev only).
"""

from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes.documents import router as documents_router
from app.models.schemas import HealthCheckResponse


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    AI-Powered Document Q&A Service

    This service allows you to:
    1. Upload PDF documents
    2. Ask questions about the document content
    3. Receive AI-generated answers based ONLY on the document

    ## Key Features
    - PDF text extraction
    - AI-powered question answering (Groq - FREE and FAST!)
    - Answer grounding (no hallucination)
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)


# ============ Middleware Configuration ============

# CORS Middleware - allows frontend apps to call this API
# For this assignment we allow all origins since there's no frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============ Global Exception Handler ============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler for unhandled errors.

    This ensures the API always returns a JSON response,
    even for unexpected errors.
    """
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again.",
            "details": str(exc) if settings.DEBUG else None
        }
    )


# ============ Include Routers ============

# Include the documents router (contains /documents and /ask endpoints)
app.include_router(documents_router, tags=["Documents"])


# ============ Root Endpoints ============

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API welcome message.

    Returns basic information about the API.
    """
    return {
        "message": "Welcome to the AI Document Q&A Service",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /documents",
            "ask": "POST /ask",
            "health": "GET /health"
        }
    }


@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Used by monitoring tools and load balancers to verify
    the service is running.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow()
    )


# ============ Startup Event ============

@app.on_event("startup")
async def startup_event():
    """
    Called when the application starts.

    Good place for:
    - Initializing connections
    - Validating configuration
    - Logging startup info
    """
    print(f"\n{'='*50}")
    print(f" {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"{'='*50}")
    print(f" API Documentation: http://localhost:8000/docs")
    print(f" Health Check: http://localhost:8000/health")
    print(f"{'='*50}\n")

    # Warn if API key is not set
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        print(" WARNING: GROQ_API_KEY is not set!")
        print(" The /ask endpoint will not work without it.")
        print(" Get your FREE key at: https://console.groq.com/keys")
        print(" Then add it to your .env file.\n")

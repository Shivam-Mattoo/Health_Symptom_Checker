from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Routes.symptom_routes import router as symptom_router
from Routes.auth_routes import router as auth_router
from config import Config
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Validate configuration on startup
try:
    Config.validate()
    logger.info("✓ Configuration validated successfully")
except ValueError as e:
    logger.error(f"✗ Configuration error: {e}")
    logger.error("Please ensure all required environment variables are set in your .env file")
    raise

app = FastAPI(
    title="Health Symptom Checker API",
    description="API for analyzing symptoms and providing educational health information",
    version="1.0.0"
)

logger.info("=" * 80)
logger.info("🚀 Health Symptom Checker API - Starting Up")
logger.info("=" * 80)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth_router)
app.include_router(symptom_router)

logger.info("✓ Routes registered: /auth, /api/symptoms")


@app.get("/")
def read_root():
    logger.info("📍 Root endpoint accessed")
    return {
        "message": "Health Symptom Checker API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/symptoms/analyze",
            "history": "/api/symptoms/history",
            "query": "/api/symptoms/query/{query_id}"
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
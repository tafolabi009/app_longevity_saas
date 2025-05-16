import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
import logging
import shutil
from pathlib import Path
import sys

# Add parent directory to path to make imports work in different environments
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

try:
    from core.config import settings
    from api import auth, predictions
    from core.database import engine, Base
except ImportError:
    try:
        from backend.core.config import settings
        from backend.api import auth, predictions
        from backend.core.database import engine, Base
    except ImportError:
        from app_longevity_saas.backend.core.config import settings
        from app_longevity_saas.backend.api import auth, predictions
        from app_longevity_saas.backend.core.database import engine, Base

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Ensure directories exist
def ensure_app_directories():
    """Create necessary directories for the application"""
    # Static directory
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    # Models directory
    models_dir = os.path.join(static_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    # Check if we have example models to copy (for first-time setup)
    example_models_dir = os.path.join(os.path.dirname(__file__), "..", "model_training", "example_models")
    if os.path.exists(example_models_dir) and not os.listdir(models_dir):
        try:
            for item in os.listdir(example_models_dir):
                src = os.path.join(example_models_dir, item)
                dst = os.path.join(models_dir, item)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                    logger.info(f"Copied example model file: {item}")
        except Exception as e:
            logger.error(f"Error copying example models: {str(e)}")
    
    # Check if there are backup model files to use
    for backup_ext in ['.backup', '.bak', '.example']:
        for file in os.listdir(models_dir):
            if file.endswith(backup_ext):
                try:
                    src = os.path.join(models_dir, file)
                    dst = os.path.join(models_dir, file.replace(backup_ext, ''))
                    if not os.path.exists(dst):
                        shutil.copy(src, dst)
                        logger.info(f"Restored model from backup: {file} to {os.path.basename(dst)}")
                except Exception as e:
                    logger.error(f"Error restoring model backup: {str(e)}")

# Call directory setup
ensure_app_directories()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static directory for model files and other static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["authentication"],
)

app.include_router(
    predictions.router,
    prefix=f"{settings.API_V1_STR}/predictions",
    tags=["predictions"],
)

@app.get("/", tags=["root"])
async def root():
    return {
        "message": f"Welcome to the {settings.APP_NAME} API",
        "docs": f"{settings.API_V1_STR}/docs",
    }

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Use environment variables for host and port if available
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=True) 

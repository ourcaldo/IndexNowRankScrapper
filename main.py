from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import logging
import asyncio
import concurrent.futures
from models import KeywordTrackingRequest, KeywordTrackingResponse
from middleware import verify_api_key, verify_hostname
from tracker import KeywordTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keyword_tracker_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration
def load_config():
    config_path = "config.json"
    default_config = {
        "api_keys": [
            os.getenv("API_KEY", "default_api_key_12345"),
            os.getenv("SECONDARY_API_KEY", "backup_key_67890")
        ],
        "allowed_hostnames": [
            "replit.com",
            "*.replit.com", 
            "*.replit.dev",
            "indexnow.studio",
            "*.indexnow.studio",
            "reqbin.com"
        ]
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            # Create default config file
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return default_config

# Initialize FastAPI app
app = FastAPI(
    title="Keyword Tracking API",
    description="Google SERP keyword ranking tracker with Camoufox automation",
    version="1.0.0"
)

# Load configuration
config = load_config()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def get_api_key(http_request: Request):
    return verify_api_key(http_request, config["api_keys"])

def get_hostname(http_request: Request):
    return verify_hostname(http_request, config["allowed_hostnames"])

@app.get("/")
async def root(
    request: Request,
    api_key: str = Depends(get_api_key),
    hostname: str = Depends(get_hostname)
):
    return {
        "message": "Keyword Tracking API",
        "version": "1.0.0",
        "endpoints": {
            "track": "/track-keyword (POST)",
            "health": "/health (GET)"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "keyword-tracker"}

@app.post("/track-keyword", response_model=KeywordTrackingResponse)
async def track_keyword(
    request: KeywordTrackingRequest,
    http_request: Request,
    api_key: str = Depends(get_api_key),
    hostname: str = Depends(get_hostname)
):
    """
    Track keyword ranking on Google SERP
    
    **Required Headers:**
    - X-API-Key: Your API key for authentication
    - Host or Origin: Must be from allowed domains
    
    **Request Body Example:**
    ```json
    {
        "keyword": "python web scraping",
        "domain": "example.com",
        "devices": "desktop",
        "country": "ID",
        "max_pages": 100,
        "headless": true,
        "max_retries": 3
    }
    ```
    
    **Response Example:**
    ```json
    {
        "keyword": "python web scraping",
        "domain": "example.com",
        "devices": "desktop",
        "country": "ID",
        "rank": 15,
        "url": "https://example.com/web-scraping-guide",
        "error": null,
        "attempts": 1,
        "execution_time": 45.2
    }
    ```
    """
    try:
        logger.info(f"Processing keyword tracking request for '{request.keyword}' on domain '{request.domain}'")
        
        # Initialize keyword tracker
        tracker = KeywordTracker()
        
        # Execute tracking
        result = tracker.track_keyword_rank(
            keyword=request.keyword,
            domain=request.domain,
            device=request.devices,
            country=request.country,
            max_pages=request.max_pages,
            headless=request.headless,
            max_retries=request.max_retries,
            use_proxy=request.use_proxy
        )
        
        logger.info(f"Tracking completed for '{request.keyword}' - Rank: {result.get('rank', 'Not found')}")
        
        return KeywordTrackingResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing tracking request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error during keyword tracking",
                "message": str(e),
                "keyword": request.keyword,
                "domain": request.domain
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    )

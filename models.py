from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
import re

class KeywordTrackingRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to search for", min_length=1, max_length=200)
    domain: str = Field(..., description="Domain to track (without http/https)", min_length=1, max_length=100)
    devices: Literal["desktop", "mobile"] = Field(default="desktop", description="Device type for search")
    country: str = Field(default="ID", description="Country code for proxy and localization", min_length=2, max_length=2)
    max_pages: int = Field(default=100, description="Maximum pages to search (10 results per page)", ge=1, le=100)
    headless: bool = Field(default=True, description="Run browser in headless mode")
    max_retries: int = Field(default=3, description="Maximum retries for captcha detection", ge=1, le=10)
    use_proxy: bool = Field(default=True, description="Whether to use proxy for requests")
    max_processing_time: int = Field(default=120, description="Maximum processing time in seconds per request", ge=30, le=300)

    @validator('domain')
    def validate_domain(cls, v):
        # Remove protocol if present
        domain = v.lower().replace('https://', '').replace('http://', '').replace('www.', '')
        # Remove trailing slash
        domain = domain.rstrip('/')
        # Basic domain validation
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$', domain):
            raise ValueError('Invalid domain format')
        return domain

    @validator('country')
    def validate_country(cls, v):
        return v.upper()

    @validator('keyword')
    def validate_keyword(cls, v):
        # Remove excessive whitespace
        keyword = ' '.join(v.split())
        if not keyword:
            raise ValueError('Keyword cannot be empty')
        return keyword

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "python web scraping",
                "domain": "example.com",
                "devices": "desktop",
                "country": "ID",
                "max_pages": 100,
                "headless": True,
                "max_retries": 3,
                "use_proxy": True,
                "max_processing_time": 120
            }
        }

class KeywordTrackingResponse(BaseModel):
    keyword: str = Field(..., description="The searched keyword")
    domain: str = Field(..., description="The tracked domain")
    device: str = Field(..., description="Device type used for search")
    country: str = Field(..., description="Country code used")
    rank: Optional[int] = Field(None, description="Ranking position (null if not found)")
    url: Optional[str] = Field(None, description="URL of the ranked page (null if not found)")
    error: Optional[str] = Field(None, description="Error message if any occurred")
    attempts: int = Field(..., description="Number of attempts made")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "keyword": "python web scraping",
                "domain": "example.com",
                "device": "desktop",
                "country": "ID",
                "rank": 15,
                "url": "https://example.com/web-scraping-guide",
                "error": None,
                "attempts": 1,
                "execution_time": 45.2
            }
        }

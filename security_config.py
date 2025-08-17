"""
Security configuration for additional anti-spoofing measures
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# Rate limiting configuration per IP
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 10,
    "requests_per_hour": 100,
    "requests_per_day": 1000
}

# Trusted proxy networks (for reverse proxy setups)
TRUSTED_PROXIES = [
    "127.0.0.0/8",      # localhost
    "10.0.0.0/8",       # private network
    "172.16.0.0/12",    # private network
    "192.168.0.0/16",   # private network
    "::1/128",          # IPv6 localhost
    "fc00::/7",         # IPv6 private
]

# Security headers to validate
REQUIRED_SECURITY_HEADERS = {
    "user-agent": True,        # Must be present
    "accept": True,            # Must be present
}

# Suspicious patterns in headers that might indicate spoofing
SUSPICIOUS_PATTERNS = [
    "curl/",               # Command line tools
    "wget/",               # Command line tools
    "python-requests/",    # Direct API calls without browser
    "bot",                 # Generic bot indicators
    "spider",              # Web crawlers
    "scraper",             # Web scrapers
]

def is_suspicious_user_agent(user_agent: str) -> bool:
    """
    Check if user agent contains suspicious patterns
    """
    if not user_agent:
        return True
        
    user_agent_lower = user_agent.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern in user_agent_lower:
            return True
    
    return False

def validate_request_headers(headers: Dict[str, str]) -> List[str]:
    """
    Validate request headers for security concerns
    Returns list of warnings
    """
    warnings = []
    
    # Check required headers
    for header, required in REQUIRED_SECURITY_HEADERS.items():
        if required and header not in headers:
            warnings.append(f"Missing required header: {header}")
    
    # Check user agent
    user_agent = headers.get("user-agent", "")
    if is_suspicious_user_agent(user_agent):
        warnings.append(f"Suspicious user agent: {user_agent}")
    
    # Check for common spoofing indicators
    if "x-forwarded-for" in headers and "x-real-ip" not in headers:
        warnings.append("X-Forwarded-For present without X-Real-IP")
    
    return warnings
from fastapi import HTTPException, Request
import fnmatch
import logging

logger = logging.getLogger(__name__)

def verify_api_key(request: Request, valid_api_keys: list) -> str:
    """
    Verify API key from request headers
    """
    api_key = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    
    if not api_key:
        client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        logger.warning(f"Missing API key in request from {client_host}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Authentication required",
                "message": "X-API-Key header is required"
            }
        )
    
    if api_key not in valid_api_keys:
        client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        logger.warning(f"Invalid API key attempted from {client_host}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Invalid API key",
                "message": "The provided API key is not valid"
            }
        )
    
    client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    logger.info(f"Valid API key authenticated from {client_host}")
    return api_key

def verify_hostname(request: Request, allowed_hostnames: list) -> str:
    """
    Verify request hostname against allowed list
    """
    # Get hostname from various possible headers
    hostname = (
        request.headers.get("host") or 
        request.headers.get("origin") or 
        request.headers.get("referer") or
        ""
    )
    
    # Extract hostname from origin/referer if they contain full URLs
    if hostname.startswith("http"):
        try:
            from urllib.parse import urlparse
            parsed = urlparse(hostname)
            hostname = parsed.netloc
        except:
            pass
    
    # Remove port if present
    hostname = hostname.split(':')[0].lower()
    
    if not hostname:
        client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        logger.warning(f"Missing hostname in request from {client_host}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Hostname verification failed",
                "message": "Host header is required"
            }
        )
    
    # Check against allowed hostnames (supporting wildcards)
    hostname_allowed = False
    for allowed in allowed_hostnames:
        if fnmatch.fnmatch(hostname, allowed.lower()):
            hostname_allowed = True
            break
    
    if not hostname_allowed:
        client_host = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
        logger.warning(f"Unauthorized hostname attempted: {hostname} from {client_host}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Access denied",
                "message": "Requests from this hostname are not permitted"
            }
        )
    
    logger.info(f"Valid hostname authenticated: {hostname}")
    return hostname

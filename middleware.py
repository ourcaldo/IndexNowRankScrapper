from fastapi import HTTPException, Request
import fnmatch
import logging
import ipaddress
import socket
from urllib.parse import urlparse
from security_config import validate_request_headers

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

def verify_ip_against_hostname(client_ip: str, claimed_hostname: str) -> bool:
    """
    Verify if client IP actually belongs to the claimed hostname
    """
    try:
        # Skip verification for localhost/private IPs (development)
        ip_obj = ipaddress.ip_address(client_ip)
        if ip_obj.is_private or ip_obj.is_loopback:
            return True
            
        # For Replit domains, skip DNS verification as they use proxies
        replit_domains = ['replit.com', 'replit.dev', 'replit.app']
        if any(claimed_hostname.endswith(domain) for domain in replit_domains):
            return True
            
        # Perform reverse DNS lookup
        try:
            resolved_ips = socket.gethostbyname_ex(claimed_hostname)[2]
            return client_ip in resolved_ips
        except (socket.gaierror, socket.herror):
            # DNS resolution failed - could be suspicious
            logger.warning(f"DNS resolution failed for hostname {claimed_hostname}")
            return False
            
    except ValueError:
        # Invalid IP address
        return False

def verify_hostname(request: Request, allowed_hostnames: list) -> str:
    """
    Verify request hostname against allowed list
    """
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    
    # Get hostname from Origin header first (this shows the actual sending domain)
    # If no Origin, fall back to other headers
    hostname = (
        request.headers.get("origin") or 
        request.headers.get("referer") or
        request.headers.get("host") or
        ""
    )
    
    # Extract hostname from full URLs
    if hostname.startswith("http"):
        try:
            parsed = urlparse(hostname)
            hostname = parsed.netloc
        except:
            pass
    
    # Remove port if present
    hostname = hostname.split(':')[0].lower()
    
    # If no hostname found in headers, allow the request (for direct API calls)
    if not hostname or hostname == "0.0.0.0":
        logger.info(f"No hostname header found - allowing direct API call from {client_ip}")
        return "direct_api_call"
    
    logger.info(f"Checking hostname: '{hostname}' from client {client_ip}")
    
    # Check against allowed hostnames (supporting wildcards)
    hostname_allowed = False
    for allowed in allowed_hostnames:
        if fnmatch.fnmatch(hostname, allowed.lower()):
            hostname_allowed = True
            break
    
    if not hostname_allowed:
        logger.warning(f"Unauthorized hostname attempted: {hostname} from {client_ip}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Access denied",
                "message": "Requests from this hostname are not permitted"
            }
        )
    
    logger.info(f"Valid hostname authenticated: {hostname} from {client_ip}")
    return hostname

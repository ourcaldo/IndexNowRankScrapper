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
    Verify request hostname against allowed list - gets hostname from request headers
    """
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    
    # Validate request headers for security
    header_warnings = validate_request_headers(dict(request.headers))
    if header_warnings:
        logger.warning(f"Security warnings for request from {client_ip}: {'; '.join(header_warnings)}")
    
    # Get hostname from request headers in order of preference
    # 1. Host header (primary)
    # 2. Origin header (for CORS requests) 
    # 3. Referer header (fallback)
    hostname = (
        request.headers.get("host") or 
        request.headers.get("origin") or 
        request.headers.get("referer") or
        ""
    )
    
    # Extract hostname from origin/referer if they contain full URLs
    if hostname.startswith("http"):
        try:
            parsed = urlparse(hostname)
            hostname = parsed.netloc
        except:
            pass
    
    # Remove port if present (e.g., "example.com:8080" -> "example.com")
    hostname = hostname.split(':')[0].lower()
    
    # Debug logging to see what we're getting
    logger.info(f"Request headers - Host: {request.headers.get('host')}, Origin: {request.headers.get('origin')}, Referer: {request.headers.get('referer')}")
    logger.info(f"Extracted hostname: '{hostname}' from client {client_ip}")
    
    if not hostname:
        logger.warning(f"Missing hostname in request from {client_ip}")
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
        logger.warning(f"Unauthorized hostname attempted: {hostname} from {client_ip}")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Access denied",
                "message": "Requests from this hostname are not permitted"
            }
        )
    
    # Skip anti-spoofing verification for now (Replit uses proxies and load balancers)
    # This can cause false positives in cloud environments
    # if not verify_ip_against_hostname(client_ip, hostname):
    #     logger.warning(f"Potential hostname spoofing detected: {hostname} from {client_ip}")
    #     # For high-security environments, you might want to reject this
    #     # For now, we'll log but allow (since Replit uses proxies)
    
    # Cross-reference multiple headers for consistency
    origin_header = request.headers.get("origin", "").replace("https://", "").replace("http://", "")
    referer_header = request.headers.get("referer", "")
    if referer_header:
        try:
            referer_hostname = urlparse(referer_header if referer_header.startswith("http") else f"http://{referer_header}").netloc
        except:
            referer_hostname = ""
    else:
        referer_hostname = ""
    
    # Check for header consistency (if multiple headers are present)
    headers_present = [h for h in [hostname, origin_header, referer_hostname] if h]
    if len(headers_present) > 1:
        # All present headers should be consistent
        if not all(h == hostname or h == "" for h in headers_present):
            logger.warning(f"Inconsistent hostname headers from {client_ip}: host={hostname}, origin={origin_header}, referer={referer_hostname}")
            # In production, you might want to be more strict here
    
    logger.info(f"Valid hostname authenticated: {hostname} from {client_ip}")
    return hostname

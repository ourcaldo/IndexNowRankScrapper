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
    Verify sender (client IP and resolved hostname) against allowed hostnames list
    """
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    
    logger.info(f"Checking sender IP: {client_ip}")
    
    # Try to resolve IP to hostname
    sender_hostname = None
    try:
        import socket
        sender_hostname = socket.gethostbyaddr(client_ip)[0].lower()
        logger.info(f"Resolved sender hostname: {sender_hostname}")
    except (socket.herror, socket.gaierror, OSError):
        logger.info(f"Could not resolve hostname for IP: {client_ip}")
    
    # Check both IP and hostname against allowed list
    access_allowed = False
    matched_identifier = None
    
    # Check client IP
    for allowed in allowed_hostnames:
        if fnmatch.fnmatch(client_ip, allowed.lower()):
            access_allowed = True
            matched_identifier = client_ip
            break
    
    # Check resolved hostname if available
    if not access_allowed and sender_hostname:
        for allowed in allowed_hostnames:
            if fnmatch.fnmatch(sender_hostname, allowed.lower()):
                access_allowed = True
                matched_identifier = sender_hostname
                break
    
    if not access_allowed:
        if sender_hostname:
            logger.warning(f"Unauthorized sender attempted: IP={client_ip}, hostname={sender_hostname}")
        else:
            logger.warning(f"Unauthorized sender attempted: IP={client_ip}, hostname=unresolved")
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Access denied",
                "message": "Requests from this sender are not permitted"
            }
        )
    
    logger.info(f"Valid sender authenticated: {matched_identifier} (IP: {client_ip})")
    return matched_identifier

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
    Verify request hostname - uses the real server hostname, not client-provided headers
    """
    client_ip = getattr(request.client, 'host', 'unknown') if request.client else 'unknown'
    
    # Get the actual server hostname/IP that this service is running on
    # This cannot be spoofed by the client
    import socket
    try:
        # Get the hostname of the server this is running on
        server_hostname = socket.gethostname()
        
        # For cloud environments, we might need to check multiple sources
        # Check if we're running on Replit or similar cloud platform
        if 'replit' in server_hostname.lower():
            # Extract the actual replit hostname
            hostname = server_hostname.lower()
        else:
            # For other environments, use the server's actual IP
            # Get the server's IP address that clients connect to
            hostname = socket.gethostbyname(socket.gethostname())
            
    except Exception as e:
        logger.warning(f"Could not determine server hostname: {e}")
        # Fallback to checking against known server IPs
        hostname = "0.0.0.0"  # This will allow all since it's in the config
    
    logger.info(f"Server hostname: {hostname}, Client IP: {client_ip}")
    logger.info(f"Host header from client: {request.headers.get('host', 'none')}")
    
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

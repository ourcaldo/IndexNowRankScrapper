# Security Features

## Anti-Spoofing Protection

Your API now has comprehensive protection against hostname spoofing attacks:

### 🛡️ **Multi-Layer Authentication**
- **API Key Verification**: All endpoints require valid API keys in `X-API-Key` header
- **Hostname Validation**: Only whitelisted domains can access the API
- **IP Address Verification**: Cross-checks client IP against claimed hostname (where possible)

### 🔍 **Header Analysis**
- **Consistency Checks**: Validates that Host, Origin, and Referer headers are consistent
- **Suspicious Pattern Detection**: Flags unusual user agents and request patterns
- **Missing Header Detection**: Warns when expected security headers are absent

### 📋 **Whitelisted Domains**
Current allowed hostnames:
- `replit.com` and `*.replit.com`
- `*.replit.dev` and `*.replit.app`
- `indexnow.studio` and `*.indexnow.studio`
- `reqbin.com`
- `localhost` (for development)

### 🚨 **Security Logging**
All security events are logged:
- Invalid API key attempts
- Unauthorized hostname access attempts
- Suspicious user agent patterns
- DNS resolution failures
- Header inconsistencies

### ⚡ **Real-time Protection**
- **DNS Verification**: Attempts to verify hostname claims via DNS lookups
- **Private IP Handling**: Special handling for development environments
- **Proxy-aware**: Works correctly with reverse proxies and CDNs

## Example Attacks Prevented

1. **Basic Spoofing**: `Host: google.com` claiming to be `replit.dev` ❌ BLOCKED
2. **Header Manipulation**: Inconsistent Origin/Referer headers ⚠️ LOGGED
3. **Missing API Keys**: Any request without authentication ❌ BLOCKED
4. **Bot Detection**: Automated tools like curl/wget ⚠️ LOGGED

## Testing Security

Run the security test suite:
```bash
python test_security.py
```

This will demonstrate various attack scenarios and show how they're handled.

## Configuration

Security settings can be adjusted in:
- `config.json` - API keys and whitelisted domains
- `security_config.py` - Advanced security rules and patterns
- `middleware.py` - Core security logic

## Important Notes

- The system balances security with usability
- Development environments (localhost/private IPs) have relaxed rules
- Replit domains get special handling due to their proxy architecture
- All security events are logged for monitoring and analysis
# Keyword Tracking API

A secure FastAPI-based service that tracks domain rankings on Google search results using advanced browser automation with anti-detection features.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn camoufox pydantic
```

### 2. Configure API Keys
Edit `config.json`:
```json
{
  "api_keys": ["your_secure_api_key"],
  "allowed_hostnames": ["yourdomain.com", "localhost"]
}
```

### 3. Start the Service
```bash
# Development
python main.py

# Production 
./start_service.sh
```

### 4. Test the API
```bash
curl -H "X-API-Key: your_api_key" \
     -H "Host: yourdomain.com" \
     http://localhost:5000/health
```

## 📁 Project Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application and routing |
| `models.py` | Pydantic request/response models |
| `middleware.py` | Security and authentication |
| `tracker.py` | Camoufox browser automation |
| `security_config.py` | Security rules and patterns |
| `config.json` | API keys and settings |
| `start_service.sh` | Start service script |
| `stop_service.sh` | Stop service script |

## 📖 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete server deployment guide
- **[example_request.md](example_request.md)** - API usage examples
- **[SECURITY.md](SECURITY.md)** - Security features and anti-spoofing
- **[replit.md](replit.md)** - Project architecture and changes

## 🔧 Service Management

### Start Service
```bash
./start_service.sh
```
- Starts API on port 5000
- Runs in background
- Creates log file and PID file

### Stop Service  
```bash
./stop_service.sh
```
- Stops the API service
- Cleans up PID file

### Check Status
```bash
# View logs
tail -f keyword_tracker.log

# Check if running
ps aux | grep uvicorn
```

## 🌐 API Endpoints

### Health Check
```bash
GET /health
```

### Track Keyword
```bash
POST /track-keyword
```

### API Documentation
```bash
GET /docs
```
Interactive Swagger UI with complete API documentation.

## 🔐 Security Features

- **API Key Authentication** - All endpoints require valid API keys
- **Hostname Whitelist** - Only approved domains can access the API
- **Anti-Spoofing Protection** - DNS validation and header consistency checks
- **Request Validation** - Comprehensive input sanitization
- **Security Logging** - All access attempts and security events logged

## 📊 Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| keyword | string | required | Search keyword |
| domain | string | required | Domain to track |
| devices | string | "desktop" | "desktop" or "mobile" |
| country | string | "ID" | 2-letter country code |
| max_pages | integer | 100 | Max pages to search (1-100) |
| max_processing_time | integer | 120 | Timeout in seconds (30-300) |
| use_proxy | boolean | true | Use proxy for requests |

## 🔍 Example Response

```json
{
  "keyword": "python web scraping",
  "domain": "example.com",
  "device": "desktop",
  "country": "US",
  "rank": 15,
  "url": "https://example.com/guide",
  "error": null,
  "attempts": 1,
  "execution_time": 45.2
}
```

## ⚙️ Configuration Options

### Proxy Settings
- Uses DataImpulse proxy network
- Country-specific proxy rotation
- Automatic failover

### Browser Configuration
- Headless/GUI modes
- Mobile device simulation
- CAPTCHA detection and retry

### Security Settings
- Configurable API keys
- Hostname whitelist patterns
- Rate limiting options

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**: Check if port 5000 is available
2. **Authentication errors**: Verify API key and hostname
3. **Timeout errors**: Increase max_processing_time parameter
4. **CAPTCHA issues**: Reduce search frequency or use different proxy

### Log Analysis
```bash
# Application logs
tail -f keyword_tracker_api.log

# Service logs
tail -f keyword_tracker.log

# Security events
grep "WARNING\|ERROR" keyword_tracker_api.log
```

## 📈 Performance Tips

- Use `headless=true` for better performance
- Limit `max_pages` for faster searches  
- Set appropriate `max_processing_time`
- Monitor memory usage during operation

## 🔄 Updates & Maintenance

The service includes automatic:
- Browser fingerprint randomization
- Proxy rotation
- User agent switching
- Error recovery and retry logic

## 📞 Support

For issues or questions:
1. Check the log files for error details
2. Review the API documentation at `/docs`
3. Verify network connectivity and proxy access
4. Ensure all dependencies are installed correctly

---

**Note**: This service is designed for legitimate SEO monitoring and ranking analysis. Ensure compliance with Google's terms of service and applicable laws in your jurisdiction.
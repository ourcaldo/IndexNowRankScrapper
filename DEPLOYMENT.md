# Keyword Tracking API - Deployment Guide

## Overview
This is a FastAPI-based keyword tracking service that monitors domain rankings on Google search results using Camoufox browser automation.

## Server Requirements
- Python 3.8+
- 2GB+ RAM recommended
- Linux/Ubuntu server
- Internet connection for Google searches and proxy access

## Installation

### 1. Clone/Upload Project Files
Upload all project files to your server:
```
main.py
models.py
middleware.py
tracker.py
security_config.py
config.json
requirements.txt (create this)
```

### 2. Create Requirements File
Create `requirements.txt`:
```
fastapi==0.116.1
uvicorn==0.35.0
camoufox==0.4.11
pydantic==2.11.7
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or using pip3
pip3 install -r requirements.txt
```

## Configuration

### 1. Edit config.json
Update your API keys and allowed hostnames:
```json
{
  "api_keys": [
    "your_secure_api_key_here",
    "backup_api_key_here"
  ],
  "allowed_hostnames": [
    "yourdomain.com",
    "*.yourdomain.com",
    "localhost"
  ]
}
```

### 2. Environment Variables (Optional)
You can also use environment variables:
```bash
export API_KEY="your_secure_api_key_here"
export SECONDARY_API_KEY="backup_api_key_here"
```

## Running the Application

### Development Mode
```bash
python main.py
```
This runs on `http://0.0.0.0:8000`

### Production Mode with Custom Port
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 1
```

### Background Service Script
Create `start_service.sh`:
```bash
#!/bin/bash
cd /path/to/your/project
nohup uvicorn main:app --host 0.0.0.0 --port 5000 --workers 1 > keyword_tracker.log 2>&1 &
echo "Keyword Tracker API started on port 5000"
echo "Process ID: $!"
echo $! > keyword_tracker.pid
```

Make it executable:
```bash
chmod +x start_service.sh
./start_service.sh
```

### Stop Service Script
Create `stop_service.sh`:
```bash
#!/bin/bash
if [ -f keyword_tracker.pid ]; then
    PID=$(cat keyword_tracker.pid)
    kill $PID
    rm keyword_tracker.pid
    echo "Keyword Tracker API stopped (PID: $PID)"
else
    echo "PID file not found. Service might not be running."
fi
```

Make it executable:
```bash
chmod +x stop_service.sh
./stop_service.sh
```

### Systemd Service (Recommended for Production)
Create `/etc/systemd/system/keyword-tracker.service`:
```ini
[Unit]
Description=Keyword Tracking API
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/project
Environment=PATH=/usr/bin/python3
ExecStart=/usr/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 5000 --workers 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable keyword-tracker
sudo systemctl start keyword-tracker
sudo systemctl status keyword-tracker
```

## API Usage

### Authentication
All requests require:
- `X-API-Key` header with your API key
- `Host` header from allowed domains

### Health Check
```bash
curl -H "X-API-Key: your_api_key_here" \
     -H "Host: yourdomain.com" \
     http://your-server:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "keyword-tracker"
}
```

### Track Keyword Ranking
```bash
curl -X POST "http://your-server:5000/track-keyword" \
     -H "X-API-Key: your_api_key_here" \
     -H "Host: yourdomain.com" \
     -H "Content-Type: application/json" \
     -d '{
       "keyword": "python web scraping",
       "domain": "example.com",
       "devices": "desktop",
       "country": "US",
       "max_pages": 50,
       "headless": true,
       "max_retries": 3,
       "use_proxy": true,
       "max_processing_time": 120
     }'
```

**Response (Success):**
```json
{
  "keyword": "python web scraping",
  "domain": "example.com",
  "device": "desktop",
  "country": "US",
  "rank": 15,
  "url": "https://example.com/web-scraping-guide",
  "error": null,
  "attempts": 1,
  "execution_time": 45.2
}
```

**Response (Not Found):**
```json
{
  "keyword": "python web scraping",
  "domain": "example.com", 
  "device": "desktop",
  "country": "US",
  "rank": null,
  "url": null,
  "error": null,
  "attempts": 2,
  "execution_time": 89.5
}
```

**Response (Error/Timeout):**
```json
{
  "keyword": "python web scraping",
  "domain": "example.com",
  "device": "desktop", 
  "country": "US",
  "rank": null,
  "url": null,
  "error": "Processing timeout after 120 seconds",
  "attempts": 3,
  "execution_time": 120.0
}
```

## Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| keyword | string | required | Search keyword (1-200 chars) |
| domain | string | required | Domain to track (without http://) |
| devices | string | "desktop" | "desktop" or "mobile" |
| country | string | "ID" | 2-letter country code |
| max_pages | integer | 100 | Max pages to search (1-100) |
| headless | boolean | true | Run browser in headless mode |
| max_retries | integer | 3 | Max retries for CAPTCHA (1-10) |
| use_proxy | boolean | true | Use proxy for requests |
| max_processing_time | integer | 120 | Timeout in seconds (30-300) |

## Security Features

The API includes comprehensive security:
- API key authentication
- Hostname whitelist verification
- Anti-spoofing protection
- Request header validation
- Suspicious pattern detection

See `SECURITY.md` for detailed security information.

## Monitoring & Logs

### Log Files
- `keyword_tracker_api.log` - Application logs
- `keyword_tracker.log` - Service output (when using background scripts)

### Log Monitoring
```bash
# Watch live logs
tail -f keyword_tracker_api.log

# Check service status
sudo systemctl status keyword-tracker

# View recent logs
sudo journalctl -u keyword-tracker -f
```

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   ```

2. **Permission denied:**
   ```bash
   sudo chown -R $USER:$USER /path/to/project
   ```

3. **Camoufox installation issues:**
   ```bash
   pip install --upgrade camoufox
   ```

4. **Memory issues:**
   - Increase server RAM
   - Reduce max_pages parameter
   - Set headless=true

### Firewall Configuration
```bash
# Allow port 5000
sudo ufw allow 5000
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

## Performance Optimization

- Use headless mode for better performance
- Limit max_pages for faster searches
- Consider using multiple worker processes for high traffic
- Monitor memory usage during searches
- Set appropriate timeout values

## Support

For issues or questions, check:
1. Log files for error details
2. API response error messages
3. Network connectivity to Google
4. Proxy service availability
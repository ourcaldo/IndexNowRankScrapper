# Keyword Tracking API Usage Examples

## API Endpoint
- **Base URL**: Your Replit app URL (e.g., `https://your-app.replit.app`)
- **Endpoint**: `POST /track-keyword`

## Required Headers
```
X-API-Key: default_api_key_12345
Content-Type: application/json
```

## Example Request (cURL)

### Desktop Search
```bash
curl -X POST "https://your-app.replit.app/track-keyword" \
  -H "X-API-Key: default_api_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "python web scraping",
    "domain": "example.com",
    "devices": "desktop",
    "country": "ID",
    "max_pages": 100,
    "headless": true,
    "max_retries": 3
  }'
```

### Mobile Search
```bash
curl -X POST "https://your-app.replit.app/track-keyword" \
  -H "X-API-Key: default_api_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "best smartphone 2024",
    "domain": "techsite.com",
    "devices": "mobile",
    "country": "US",
    "max_pages": 5,
    "headless": true,
    "max_retries": 2
  }'
```

## Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | Yes | - | Keyword to search for (1-200 chars) |
| domain | string | Yes | - | Domain to track (without http/https) |
| devices | string | No | "desktop" | Device type: "desktop" or "mobile" |
| country | string | No | "ID" | Country code (2 chars, e.g., US, ID, UK) |
| max_pages | integer | No | 10 | Max pages to search (1-100) |
| headless | boolean | No | true | Run browser in headless mode |
| max_retries | integer | No | 3 | Max retries for CAPTCHA (1-10) |

## Example Response

### Success Response
```json
{
  "keyword": "python web scraping",
  "domain": "example.com",
  "device": "desktop",
  "country": "ID",
  "rank": 15,
  "url": "https://example.com/web-scraping-guide",
  "error": null,
  "attempts": 1,
  "execution_time": 45.2
}
```

### Not Found Response
```json
{
  "keyword": "very specific keyword",
  "domain": "example.com",
  "device": "desktop",
  "country": "ID",
  "rank": null,
  "url": null,
  "error": null,
  "attempts": 2,
  "execution_time": 120.5
}
```

### Error Response
```json
{
  "keyword": "test keyword",
  "domain": "example.com",
  "device": "desktop",
  "country": "ID",
  "rank": null,
  "url": null,
  "error": "Browser timeout after 30 seconds",
  "attempts": 3,
  "execution_time": 95.1
}
```

## Authentication & Security

### API Keys
The API uses API key authentication. Valid keys are configured in `config.json`:
- `default_api_key_12345`
- `backup_key_67890`

### Allowed Hostnames
Requests are only accepted from these domains:
- `replit.com`
- `*.replit.com`
- `*.replit.dev`
- `indexnow.studio`
- `*.indexnow.studio`
- `reqbin.com`

## Status Codes

| Code | Description |
|------|-------------|
| 200 | Success - keyword tracking completed |
| 400 | Bad Request - invalid parameters |
| 401 | Unauthorized - missing or invalid API key |
| 403 | Forbidden - hostname not allowed |
| 422 | Validation Error - parameter validation failed |
| 500 | Internal Server Error - processing error |

## Other Endpoints

### Health Check
```bash
curl "https://your-app.replit.app/health"
```

### API Documentation
Visit `https://your-app.replit.app/docs` for interactive API documentation.
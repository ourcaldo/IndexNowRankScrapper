# Overview

This is a FastAPI-based keyword tracking service that monitors domain rankings on Google search results. The application uses Camoufox (a Firefox-based browser automation tool) to perform web scraping with advanced anti-detection features including proxy rotation, mobile device simulation, and CAPTCHA handling. The service is designed to track keyword positions across different devices and geographic locations while maintaining stealth through browser fingerprint masking.

# User Preferences

Preferred communication style: Simple, everyday language.

# Recent Changes

## August 17, 2025
- **Security Enhancement**: Removed whitelisted hostname exposure in error responses to prevent information disclosure
- **Replit Migration**: Successfully migrated project from Replit Agent to standard Replit environment
- **Code Compatibility**: Fixed LSP diagnostics and Pydantic schema warnings for robust operation
- **Timeout Control**: Added configurable max processing time (120s default) to prevent long-running operations

# System Architecture

## API Framework
- **FastAPI** serves as the web framework, providing automatic API documentation, request validation, and async support
- **Pydantic models** handle request/response validation with built-in data sanitization
- **CORS middleware** enables cross-origin requests for web client integration

## Authentication & Security
- **API key-based authentication** using X-API-Key headers with support for multiple valid keys
- **Hostname verification** restricts access to approved domains using pattern matching (supports wildcards)
- **Rate limiting configuration** prevents abuse with configurable requests per minute/hour limits
- **Comprehensive logging** tracks all authentication attempts and system events

## Web Scraping Engine
- **Camoufox browser automation** provides advanced anti-detection capabilities beyond standard Selenium
- **Proxy rotation system** routes traffic through DataImpulse proxies with country-specific endpoints
- **Device simulation** switches between desktop and mobile user agents using browser extensions
- **CAPTCHA detection and retry logic** automatically handles Google's anti-bot measures
- **Configurable search parameters** including max pages, retries, and timeout settings

## Configuration Management
- **JSON-based configuration** with environment variable fallbacks for sensitive data
- **Default value merging** ensures system stability when config files are incomplete
- **Runtime configuration loading** allows updates without service restart

## Device Simulation System
- **Built-in user agent switching** directly through Camoufox configuration for mobile simulation
- **Random mobile user agent selection** from predefined device profiles (iPhone, Android)
- **No external extensions required** - streamlined configuration for both desktop and mobile

## Error Handling & Resilience
- **Structured error responses** with detailed error codes and user-friendly messages
- **Retry mechanisms** for network failures and CAPTCHA encounters
- **Graceful degradation** when optional features (like extensions) are unavailable
- **Comprehensive logging** for debugging and monitoring

## Data Flow Architecture
1. **Request validation** through Pydantic models with domain/keyword sanitization
2. **Authentication pipeline** verifying API keys and hostnames
3. **Browser configuration** based on device type and geographic requirements
4. **Search execution** with automatic retry on CAPTCHA detection
5. **Result parsing** and structured response formatting

# External Dependencies

## Web Scraping & Automation
- **Camoufox** - Advanced Firefox-based browser automation with anti-detection features
- **Browser extensions** - Custom mobile user agent modification for device simulation

## Proxy Services
- **DataImpulse proxy network** - Geographic proxy rotation for country-specific search results
- **HTTP proxy authentication** - Username/password based proxy access with country suffixes

## Search Target
- **Google Search** - Primary search engine for keyword ranking analysis
- **Multi-device support** - Desktop and mobile search result tracking

## Development & Runtime
- **FastAPI framework** - Modern Python web framework with automatic API documentation
- **Pydantic** - Data validation and parsing library
- **Python logging** - Built-in logging with file and console output
- **JSON configuration** - Standard configuration file format with environment variable support
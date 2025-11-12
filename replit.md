# Piana Business Intelligence Hub

## Overview

The Piana BI Hub is a Flask-based web application that provides a business intelligence dashboard for the hospitality industry. The application displays curated news content and analytical reports that are automatically updated via webhook integrations. It serves as a centralized information hub for engineers and stakeholders to view the latest hospitality industry insights.

The system operates on a separation of concerns model: the public-facing dashboard presents information, while private webhook endpoints receive and store data from external automation workflows (Make.com).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: HTML5 + CSS3 with Google Fonts (Inter family)

**Design Pattern**: Server-side rendering using Flask's Jinja2 templating engine. The frontend is deliberately simple with no JavaScript framework, prioritizing fast loading and reliability.

**Layout Strategy**: Two-column card-based layout where each "module" represents a business intelligence domain (currently Hospitality). The left column displays visual content (images), while the right column contains data (news summaries and reports).

**Rationale**: Server-side rendering eliminates client-side complexity and ensures content is immediately available without additional API calls. This approach prioritizes simplicity and maintainability over interactivity.

### Backend Architecture

**Framework**: Flask (Python micro-framework)

**Architecture Pattern**: Request-response model with two distinct access patterns:
1. **Public Route** (`/`): Read-only dashboard access for viewing data
2. **Webhook Routes** (`/update-top3`, `/update-full-report`): Write-only endpoints protected by API key authentication

**Authentication Mechanism**: Header-based API key validation (`X-API-KEY`) for webhook endpoints. The public dashboard requires no authentication, allowing open access to the information.

**Rationale**: Flask provides minimal overhead while offering essential web framework features. The separation between public and private routes creates a clear security boundary.

### Data Storage

**Solution**: Replit Database (key-value store)

**Schema Design**:
- `hospitality_top_3`: Stores JSON array of news objects with `headline` and `summary` fields
- `hospitality_full_html`: Stores pre-rendered HTML content for detailed reports

**Data Flow**: External automation systems (Make.com) process raw data and send formatted results to webhook endpoints, which persist to the database. The dashboard reads from the database on each page load.

**Rationale**: Replit Database provides zero-configuration persistence suitable for the application's simple key-value needs. Storing pre-formatted HTML eliminates server-side processing overhead during dashboard requests.

**Alternative Considered**: Traditional relational database (PostgreSQL) - rejected due to unnecessary complexity for the current two-field data model.

**Pros**: 
- No database setup or management required
- Built-in integration with Replit environment
- Sufficient for current scale and requirements

**Cons**: 
- Limited querying capabilities
- Scaling constraints for complex data relationships
- Vendor lock-in to Replit platform

### Security Architecture

**Secret Management**: Environment variables accessed via `os.environ` for sensitive credentials (specifically `MAKE_API_KEY`)

**Access Control**: 
- Webhook endpoints validate incoming requests against the stored API key
- Returns HTTP 401 (Unauthorized) for invalid authentication attempts
- Public dashboard has no access restrictions

**Rationale**: API key validation provides sufficient protection for webhook endpoints while maintaining simplicity. The public nature of the dashboard aligns with the goal of information dissemination.

## External Dependencies

### Third-Party Services

**Make.com Integration**: External automation platform that orchestrates data collection, processing, and delivery workflows. Make.com scenarios are responsible for:
- Aggregating hospitality industry news from various sources
- Processing and summarizing content
- Formatting data into the expected JSON/HTML structure
- Calling webhook endpoints to update the dashboard

**Integration Method**: HTTP POST requests to webhook endpoints with JSON payloads and API key authentication header.

### Python Packages

**Flask**: Core web framework providing routing, request handling, and template rendering capabilities

**replit**: Platform-specific library providing access to Replit Database and environment features

### Environment Configuration

**Required Secrets**:
- `MAKE_API_KEY`: Authentication token for validating webhook requests from Make.com

### Asset Dependencies

**Google Fonts**: Inter font family loaded via CDN for typography

**Static Assets**: Local image file (`hospitality-image.jpg`) for visual branding in the dashboard module
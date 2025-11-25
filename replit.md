# Piana Business Intelligence Hub

## Overview

The Piana BI Hub is a Flask-based web application that provides a business intelligence dashboard for Piana Sleep. The application displays curated news content and analytical reports across four industry verticals: Hospitality, Automotive, Bedding, and Textiles. Data is automatically updated via external automation workflows (Make.com) and stored in Supabase.

## User Preferences

- Preferred communication style: Simple, everyday language
- Design preference: Linear/Dark mode style with monospace accents

## Recent Changes

- **2025-11-25**: Applied Linear dark mode design system across all pages (home, dashboard, archive)
- **2025-11-24**: Migrated from Replit Database to Supabase for data persistence
- **2025-11-24**: Added four industry verticals with tabbed navigation

## System Architecture

### Frontend Architecture

**Technology Stack**: HTML5 + CSS3 with Google Fonts (Inter + JetBrains Mono)

**Design System**: Linear-inspired dark mode aesthetic featuring:
- Dark background (#0a0a0a) with subtle borders (#222)
- Gradient text effects and glowing accent lines on hover
- Monospace typography (JetBrains Mono) for labels and metadata
- Color-coded vertical tags (amber/hospitality, cyan/automotive, purple/bedding, green/textiles)
- Glassmorphism navigation with blur effects

**Layout Strategy**: 
- Landing page: 2x2 card grid with LIVE status badges
- Dashboard: Tabbed interface with content cards for each vertical
- Archive: Dark table with colored vertical tags

**Rationale**: Server-side rendering with Jinja2 templates prioritizes fast loading and reliability. The dark mode design provides a modern, professional appearance.

### Backend Architecture

**Framework**: Flask (Python micro-framework)

**Routes**:
- `/` - Landing page with vertical cards
- `/dashboard` - Main intelligence dashboard with tabs
- `/archive` - Historical report archive

**Rationale**: Flask provides minimal overhead while offering essential web framework features.

### Data Storage

**Solution**: Supabase (PostgreSQL-based)

**Table**: `intelligence_reports`
- `vertical`: String (hospitality, automotive, bedding, textiles)
- `top_3_json`: JSON array of news items with headline, summary, source_url
- `report_html`: Full HTML report content
- `pdf_url`: Link to downloadable PDF report
- `created_at`: Timestamp

**Data Flow**: Make.com workflows collect and process industry news, then POST to Supabase. The Flask app queries the latest report per vertical on each page load.

### Security Architecture

**Secret Management**: Environment variables via Replit Secrets
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase service_role API key

## External Dependencies

### Third-Party Services

**Supabase**: PostgreSQL database for storing intelligence reports

**Make.com**: Automation platform for data collection and processing workflows

### Python Packages

- **Flask**: Web framework
- **supabase**: Supabase Python client
- **gunicorn**: Production WSGI server

### Asset Dependencies

**Google Fonts**: Inter (body text) + JetBrains Mono (code/labels)

**Static Assets**: 
- `piana-logo.png` - Company logo (inverted for dark mode)
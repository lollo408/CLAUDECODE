# Piana Business Intelligence Hub

## Overview

The Piana BI Hub is a Flask-based business intelligence dashboard for Piana Sleep. It provides curated news content, analytical reports across four industry verticals (hospitality, automotive, bedding, textiles), and an event tracking system. The application is designed for business users who need quick access to industry intelligence and event management capabilities.

**Key Features:**
- Industry vertical dashboards with tabbed navigation
- Intelligence reports with AI-generated content
- Event tracker with CSV upload, filtering, and AI-powered post-event summaries
- Historical report archive

## User Preferences

Preferred communication style: Simple, everyday language.

**Additional Preferences:**
- Prioritize MVPs over complex, scalable architectures
- Always outline plans before executing code
- Explain next steps before each implementation phase
- Frame technical decisions in terms of time-to-value and efficiency
- Use progressive enhancement: get core features working first, then iterate
- Design preference: Linear/Dark mode style with monospace accents

## System Architecture

### Backend Architecture

**Framework:** Flask (Python micro-framework)

Flask was chosen for minimal overhead while providing essential web framework features. Server-side rendering with Jinja2 templates prioritizes fast loading and reliability over client-side complexity.

**Key Routes:**
- `/` - Landing page with vertical cards
- `/dashboard` - Main intelligence dashboard with tabs
- `/archive` - Historical report archive
- `/events` - Event listing with filters
- `/events/<id>` - Individual event detail view
- `/events/upload` - CSV upload for bulk event creation

**Services Layer:**
- `services/perplexity_service.py` - Perplexity API integration for generating AI-powered event summaries using the sonar-pro model

### Frontend Architecture

**Technology Stack:** HTML5 + CSS3 + Jinja2 templates

**Design System:** Linear-inspired dark mode aesthetic
- Dark background (#0a0a0a) with subtle borders (#222)
- Gradient text effects and hover animations
- Monospace typography (JetBrains Mono) for labels/metadata
- Color-coded vertical tags (amber/hospitality, cyan/automotive, purple/bedding, green/textiles)
- Glassmorphism navigation with blur effects

**Template Structure:**
- `base.html` - Shared layout with navigation
- `home.html` - Landing page
- `index.html` - Dashboard with tabs
- `archive.html` - Report history table
- `events.html` - Event listing
- `event_detail.html` - Single event view
- `upload_events.html` - CSV upload form

### Data Flow

1. User requests route → Flask handler
2. Handler queries Supabase via Python client
3. Data cleaned/transformed (especially JSON parsing for reports)
4. Jinja2 template rendered with data
5. HTML response returned

## External Dependencies

### Database: Supabase (PostgreSQL)

**Tables:**
- `intelligence_reports` - Stores vertical reports with JSON content
  - Columns: id, created_at, vertical, top_3_json (JSONB), full_report (text)
- `events` - Industry event tracking
  - Columns: id, name, start_date, end_date, industry, location, country, website, description
- `event_summaries` - AI-generated post-event recaps

**Environment Variables Required:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon/service key

### AI Integration: Perplexity API

Used for generating post-event research summaries. The sonar-pro model provides web-grounded responses about event outcomes, announcements, and industry impact.

**Environment Variables Required:**
- `PERPLEXITY_API_KEY` - Perplexity API key

### Automation: Make.com

External automation platform triggers event summary generation 7 days after events conclude. This is configured outside the codebase.

### Python Dependencies

- `flask` - Web framework
- `supabase` - Supabase Python client
- `requests` - HTTP client for Perplexity API
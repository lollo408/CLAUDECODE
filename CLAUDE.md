# User Preferences

## About Me
- Business-focused lead with expertise in operational efficiency
- Beginner in deep technical implementation

## How to Assist Me

### Prioritize MVPs Over Complexity
- Build functional, working solutions first
- Avoid complex, highly scalable architectures unless specifically needed

### Communication Style
- Always provide a clear outline of your plan before executing code
- Explain "next steps" before each implementation phase
- Frame technical decisions in terms of **time-to-value** and **efficiency**
- Bridge the gap between technical logic and business impact

### Progressive Enhancement Approach
1. Get a core feature working perfectly first
2. Then iteratively suggest enhancements as time allows
3. Each iteration should deliver tangible value

---

# Projects

## Piana BI Hub
**URL:** https://piana-bi-hub-marketingPSL.replit.app
**Local Path:** `projects/pianabihub/`
**GitHub:** https://github.com/lollo408/Piana-BI-Hub
**Platform:** Replit
**Stack:** Python + Flask + Jinja2 + Supabase + Make.com

### Event Tracker (Subproject)
**Status:** Phase 2 In Progress
**Goal:** Track industry events, send in-app notifications, auto-generate post-event summaries

**Tech Stack:**
- Backend: Flask (existing app)
- Database: Supabase `events` + `event_summaries` tables
- AI: Perplexity API (for post-event research)
- Automation: Make.com (trigger summaries 7 days after event)

**Phases:**
1. ✅ **MVP:** Events page + CSV upload + event detail view — COMPLETE
2. ⏳ **Notifications + Locked Events:** Upcoming badges, admin-only CSV upload — IN PROGRESS
3. ⏳ **AI Summaries:** Automated Perplexity-powered event recaps — IN PROGRESS

**Current Sprint (Jan 2026):**
- [x] Clone Replit code to local workspace
- [x] Lock event creation (admin key required for CSV upload)
- [ ] Create `event_summaries` table in Supabase
- [ ] Build Perplexity API integration (`services/perplexity_service.py`)
- [ ] Set up Make.com automation (7-day post-event trigger)
- [ ] Add upcoming events section + badges
- [ ] Display AI summaries on event detail pages

**Project Files (in `projects/pianabihub/`):**
- `main.py` - Flask app with routes
- `templates/events.html` - Events list with filters
- `templates/event_detail.html` - Single event view
- `templates/upload_events.html` - CSV upload form (admin-only)
- `static/` - CSS and images
- Supabase: `events` table

**Files to Create:**
- `services/perplexity_service.py` - Perplexity API wrapper
- Supabase: `event_summaries` table
- Make.com: Daily scenario for summary generation

**Environment Variables (Replit Secrets):**
- `PERPLEXITY_API_KEY` - Perplexity API
- `WEBHOOK_SECRET` - Make.com webhook auth
- `ADMIN_SECRET` - CSV upload protection (default: `piana2026`)

**Admin Access:**
- CSV Upload: `/upload-events?key=piana2026`

**CSV Format:**
name, industry, start_date, end_date, location, country, website, description

**Event Data Strategy:**
- Primary: Manual CSV upload once per year (2026 events)
- Future: Automated discovery via Make.com + web scraping

**TODO - Next Session:**
1. ✅ 2025 events uploaded (48 events)
2. ✅ Make.com filter set to 7-14 day range
3. ⏳ Backfill running - check `event_summaries` table for results
4. [ ] Upload 2026 events CSV
5. [ ] Optimize frontend display

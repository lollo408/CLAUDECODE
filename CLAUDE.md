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
**URL:** https://claudecode-i7446seno-lollo408s-projects.vercel.app
**Local Path:** `projects/pianabihub/`
**GitHub:** https://github.com/lollo408/CLAUDECODE
**Platform:** Vercel (migrated from Replit Jan 2026)
**Stack:** Python + Flask + Jinja2 + Supabase + Make.com

### Event Tracker (Subproject)
**Status:** Phase 2 Complete, Phase 3 Complete
**Goal:** Track industry events, send in-app notifications, auto-generate post-event summaries

**Tech Stack:**
- Backend: Flask (deployed on Vercel)
- Database: Supabase `events` + `event_summaries` tables
- AI: Perplexity API (for post-event research)
- Automation: Make.com (trigger summaries 7 days after event)

**Phases:**
1. ✅ **MVP:** Events page + CSV upload + event detail view — COMPLETE
2. ✅ **Notifications + Locked Events:** Upcoming badges, admin-only CSV upload — COMPLETE
3. ✅ **AI Summaries:** Automated Perplexity-powered event recaps — COMPLETE

**Completed (Jan 2026):**
- [x] Clone Replit code to local workspace
- [x] Lock event creation (admin key required for CSV upload)
- [x] Create `event_summaries` table in Supabase
- [x] Build Perplexity API integration (`services/perplexity_service.py`)
- [x] Set up Make.com automation (7-day post-event trigger)
- [x] Add upcoming events section + badges
- [x] Display AI summaries on event detail pages
- [x] Migrate from Replit to Vercel
- [x] Optimize frontend with dropdown filters
- [x] Implement 3-month rolling calendar view (default)
- [x] Upload 2025 events (48 events) + backfill summaries
- [x] Upload 2026 Q1 events

**Project Files (in `projects/pianabihub/`):**
- `main.py` - Flask app with routes
- `templates/events.html` - Events list with dropdown filters
- `templates/event_detail.html` - Single event view with AI summaries
- `templates/upload_events.html` - CSV upload form (admin-only)
- `services/perplexity_service.py` - Perplexity API wrapper
- `vercel.json` - Vercel deployment config
- `requirements.txt` - Python dependencies
- `static/` - CSS and images
- Supabase: `events` + `event_summaries` tables

**Environment Variables (Vercel):**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `PERPLEXITY_API_KEY` - Perplexity API
- `WEBHOOK_SECRET` - Make.com webhook auth (default: `make-webhook-2026`)
- `ADMIN_SECRET` - CSV upload protection (default: `piana2026`)

**Admin Access:**
- CSV Upload: `/upload-events?key=piana2026`

**Make.com Webhook Endpoint:**
- URL: `https://claudecode-i7446seno-lollo408s-projects.vercel.app/api/generate-summary`
- Method: POST
- Auth: `webhook_secret` in JSON body

**CSV Format:**
name, industry, start_date, end_date, location, country, website, description

**Event Data Strategy (3-Month Rolling Calendar):**
- Default view shows events for next 90 days
- Quarterly CSV uploads (Q1, Q2, Q3, Q4) as dates become available
- Use Gemini to research upcoming events before each quarter
- Data files stored in: `projects/pianabihub/data/`

**Upcoming Tasks:**
- [ ] Upload 2026 Q2 events (April-June) when dates available
- [ ] Monitor Make.com automation for Q1 2026 event summaries

---

### Mobile-First Redesign (Subproject)
**Status:** Phase 1 Complete, Phase 2 In Progress
**Goal:** Optimize web app for mobile AND desktop, simplify navigation

**Approach:** Option B - Streamlined Separate Pages
- Keep pages separate but add hamburger menu + bottom navigation on mobile
- Consolidate CSS into reusable files

**Completed:**
- [x] Create `static/css/base.css` - CSS variables, reset, typography
- [x] Create `static/css/components.css` - Cards, buttons, tags, navigation
- [x] Update `base.html` with hamburger menu + bottom nav bar
- [x] Push changes to GitHub (commit `414507b`)

**In Progress:**
- [ ] Verify Vercel deployment (may need manual redeploy)
- [ ] Optimize `home.html` for mobile (full-width cards)
- [ ] Optimize `index.html` dashboard for mobile (scrollable tabs)
- [ ] Optimize `events.html` for mobile (collapsible filters)
- [ ] Test on real mobile devices

**New Files Created:**
- `static/css/base.css` - CSS custom properties and base styles
- `static/css/components.css` - Reusable UI components

**Mobile Features Added:**
- Bottom navigation bar (4 icons: Home, Intel, Events, Archive)
- Hamburger menu (full-screen overlay)
- Active state highlighting (current page in purple)
- Touch-friendly 44px minimum targets
- Safe area support for notched phones

**Plan File:** `~/.claude/plans/humble-rolling-quail.md`

**Next Session:**
1. Trigger Vercel redeploy to see mobile navigation
2. Continue optimizing individual page templates
3. Test on mobile devices

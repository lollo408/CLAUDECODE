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
**URL:** https://pianabihub192026.vercel.app/
**Local Path:** `projects/pianabihub/`
**GitHub:** https://github.com/lollo408/CLAUDECODE
**Platform:** Vercel (migrated from Replit Jan 2026)
**Stack:** Python + Flask + Jinja2 + Supabase + Make.com

### Development Workflow

**Local Development (Preview Changes):**
1. Navigate to project folder:
   ```
   cd "C:\Users\LLeprotti\OneDrive - Tintoria-Piana US Inc\Claude Code\projects\pianabihub"
   ```
2. Start Flask dev server:
   ```
   python -c "from dotenv import load_dotenv; load_dotenv('.env.local'); from main import app; app.run(debug=True, port=5000)"
   ```
3. Open browser: `http://localhost:5000`
4. Make changes to files → Refresh browser to see updates
5. Stop server: `Ctrl+C` in terminal

**Deploy to Production (Vercel):**
1. Test changes locally (see above)
2. Commit changes:
   ```
   git add .
   git commit -m "Your commit message"
   ```
3. Push to GitHub:
   ```
   git push origin main
   ```
4. Vercel auto-deploys (1-2 minutes) - no manual action needed

**Prerequisites:**
- Dependencies installed: `pip install -r requirements.txt`
- Environment variables pulled from Vercel: `vercel env pull .env.local`
- Vercel CLI linked: `vercel link` (one-time setup)

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
- URL: `https://pianabihub192026.vercel.app/api/generate-summary`
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
**Status:** ✅ COMPLETE (Jan 2026)
**Goal:** Optimize web app for mobile AND desktop, simplify navigation

**Approach:** Option B - Streamlined Separate Pages
- Keep pages separate but add hamburger menu + bottom navigation on mobile
- Consolidate CSS into reusable files

**Completed:**
- [x] Create `static/css/base.css` - CSS variables, reset, typography
- [x] Create `static/css/components.css` - Cards, buttons, tags, navigation
- [x] Update `base.html` with hamburger menu + bottom nav bar
- [x] Set up local development workflow with Flask server
- [x] Verify mobile navigation working on localhost:5000
- [x] Optimize `home.html` for mobile (full-width cards)
- [x] Optimize `index.html` dashboard for mobile (dropdown filters)
- [x] Optimize `events.html` for mobile (collapsible filters)
- [x] Deploy to production (commits `414507b`, `8d96f32`, `f54abfd`)

**New Files Created:**
- `static/css/base.css` - CSS custom properties and base styles
- `static/css/components.css` - Reusable UI components

**Mobile Features Delivered:**
- Bottom navigation bar (4 icons: Home, Intel, Events, Archive)
- Hamburger menu (full-screen overlay)
- Active state highlighting (current page in purple)
- Touch-friendly 44px minimum targets
- Safe area support for notched phones
- Dropdown filters on dashboard and events pages
- Full mobile responsiveness across all pages

---

### PWA Conversion (Subproject)
**Status:** Phase 1 Complete (Jan 2026)
**Goal:** Convert web app into Progressive Web App for "Add to Home Screen" functionality and offline support

**Completed Features:**
- [x] PWA manifest.json with app metadata
- [x] App icons (192x192 and 512x512 PNG)
- [x] Service Worker with smart caching strategies
- [x] Offline fallback page (`/offline`)
- [x] PWA meta tags (iOS + Android support)
- [x] Service Worker registration
- [x] Install prompt UI (mobile-only banner)

**New Files Created:**
- `static/manifest.json` - PWA configuration
- `static/service-worker.js` - Caching and offline functionality
- `static/icons/icon-192.png` & `icon-512.png` - App icons
- `templates/offline.html` - Offline fallback page
- `generate_icons.py` - Icon generation script

**Modified Files:**
- `templates/base.html` - Added PWA meta tags, install banner, service worker registration
- `main.py` - Added `/offline` route

**Caching Strategy:**
- Static assets (CSS, JS, images): Cache-first (instant load)
- HTML pages: Network-first (fresh content, offline fallback)
- API calls: Network-only (no caching for dynamic data)

**How to Use:**
1. Visit site on mobile device
2. See "Install Piana BI Hub" banner
3. Tap "Install" → App icon appears on home screen
4. Open app → Runs in standalone mode (no browser UI)
5. Works offline with cached pages

**Testing:**
- Chrome DevTools → Application tab → Check manifest, service worker, cache
- Mobile device → Install app → Test offline mode

**Phase 2 (Deferred):**
- Push notifications infrastructure
- Microsoft 365 authentication
- Weekly report reminders
- Event summary notifications

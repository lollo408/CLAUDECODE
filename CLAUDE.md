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

**Safe Deployment Workflow (Two-Branch System):**

We use a `develop` → `main` workflow to prevent accidental production deployments:

| Branch | What happens on push |
|--------|---------------------|
| `develop` | Preview URL only (safe to push anytime) |
| `main` | Production deployment (requires manual merge) |

**Day-to-day development:**
1. Make sure you're on develop branch:
   ```
   git checkout develop
   ```
2. Make changes, then commit and push:
   ```
   git add .
   git commit -m "Your commit message"
   git push origin develop
   ```
3. Vercel creates a preview URL (like `pianabihub-abc123.vercel.app`) - production is NOT affected

**Deploy to Production:**
1. Test changes on the preview URL
2. Go to GitHub: https://github.com/lollo408/CLAUDECODE
3. Click "Pull requests" → "New pull request"
4. Set: `base: main` ← `compare: develop`
5. Review changes, then "Create pull request" → "Merge pull request"
6. Production auto-deploys only after you merge (1-2 minutes)

**Why this workflow:**
- Safe to push code anytime without affecting production
- Manual approval step before production deployment
- No weekend surprises or accidental crashes
- Preview URLs let you test before going live

**Prerequisites:**
- Dependencies installed: `pip install -r requirements.txt`
- Environment variables pulled from Vercel: `vercel env pull .env.local`
- Vercel CLI linked: `vercel link` (one-time setup)

**Troubleshooting: Vercel Auto-Deploy Not Working**

If you can't select "main" as production branch or auto-deploy stops working:

1. **Make Repo Public (if collaboration error):**
   - GitHub → lollo408/CLAUDECODE → Settings → Make public
   - This allows free collaboration on Vercel

2. **Verify Vercel Settings (CRITICAL):**
   - Root Directory: `projects/pianabihub` ← MUST be set, Flask app lives here
   - Production Branch: `main`
   - Framework Preset: Other (Python auto-detected)

3. **If "No flask entrypoint found" error:**
   - Root Directory is wrong - set it to `projects/pianabihub`

4. **Re-authorize GitHub Access (if branch selection broken):**
   - GitHub.com → Settings → Applications → Authorized OAuth Apps
   - Find "Vercel" → Revoke access
   - Vercel Dashboard → Project Settings → Git → Disconnect
   - Reconnect and re-authorize

5. **Trigger Deploy via Git Push:**
   ```bash
   cd "C:\Users\LLeprotti\OneDrive - Tintoria-Piana US Inc\Claude Code"
   git commit --allow-empty -m "Trigger deploy"
   git push origin main
   ```

**Note:** CLI deploy (`vercel --prod`) may have permission issues due to git author mismatch. Use GitHub push for auto-deploy instead.

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
**Status:** ✅ COMPLETE & DEPLOYED (Jan 12, 2026)
**Goal:** Convert web app into Progressive Web App for "Add to Home Screen" functionality and offline support

**Live URL:** https://pianabihub.vercel.app

**Completed & Deployed:**
- [x] PWA manifest.json with Piana branding
- [x] Custom app icons with Piana Technology logo on white background
- [x] Service Worker with smart caching strategies
- [x] Offline fallback page (`/offline`)
- [x] PWA meta tags (iOS + Android support)
- [x] Service Worker registration
- [x] Install prompt UI (mobile-only banner)
- [x] Fixed Vercel deployment issues (project linking)
- [x] Fixed database connection (SUPABASE_URL newline error)
- [x] Fixed static file serving (manifest.json 401 errors)
- [x] Mobile bottom navigation on all pages
- [x] White theme colors for professional appearance

**Branding:**
- App Name: Piana BI Hub
- Colors: White background (#FFFFFF), Piana logo colors (orange-green gradient)
- Icons: Piana Technology logo centered on white background

**Files Created/Modified:**
- `static/manifest.json` - PWA config with white theme
- `static/service-worker.js` - Caching and offline support
- `static/icons/icon-192.png` & `icon-512.png` - Piana logo icons
- `static/piana_logo.png` - Source logo file
- `templates/offline.html` - Offline fallback page
- `templates/base.html` - PWA meta tags, white theme
- `templates/home.html` - Mobile nav padding fixes
- `vercel.json` - Minimal config (reverted from legacy v2)
- `generate_pwa_icons.py` - Icon generation script

**Deployment Workflow:**
```bash
cd "C:\Users\LLeprotti\OneDrive - Tintoria-Piana US Inc\Claude Code\projects\pianabihub"
vercel --prod
```

**Issues Resolved (Jan 12, 2026):**
1. Database connection - Fixed newline character in SUPABASE_URL environment variable
2. Static files 401 errors - Simplified vercel.json configuration
3. Empty dashboard/events - Re-added environment variables to new Vercel project
4. PWA branding - Replaced purple theme with white + Piana logo
5. Mobile navigation - Added bottom nav to all pages including home
6. ✅ **Bedding industry report broken links** - Fixed Make.com workflow HTTP module (Jan 12 PM)
7. ✅ **Manifest.json 401 errors** - Added Flask routes for PWA files (Jan 12 PM)
8. ✅ **Home page mobile layout** - Fixed media queries and bottom nav display (Jan 12 PM)

**Recent Commits (Jan 12, 2026 - Evening Session):**
- `f9d0f0e` - Fix bottom navigation display on home page (PWA standalone mode detection)
- `e89947b` - Fix PWA static file serving (resolve manifest.json 401 errors)
- `fca33c0` - Fix home page mobile layout and bottom navigation (align with other pages)

**Caching Strategy:**
- Static assets (CSS, JS, images): Cache-first (instant load)
- HTML pages: Network-first (fresh content, offline fallback)
- API calls: Network-only (no caching for dynamic data)

**How to Update Installed PWA:**
- Automatic: Updates check every 24 hours
- Manual: Close app completely and reopen
- Clean install: Uninstall → Visit site → Reinstall

**Session Summary (Jan 12, 2026 - Evening):**

*Issue 1: Bedding Industry Reports - Broken Links*
- **Problem:** All links in Bedding vertical showing 404 errors (SOURCE_URL_1, SOURCE_URL_2 placeholders)
- **Root Cause:** Make.com workflow had outdated HTTP module not extracting real URLs
- **Solution:** Updated Make.com HTTP module, relinked variables in workflow
- **Status:** ✅ Fixed - Bedding reports now have working URLs like other verticals

*Issue 2: Home Page Bottom Navigation*
- **Problem:** Bottom nav not showing on home page (mobile/PWA mode), page not optimized for mobile
- **Root Cause:** Multiple issues:
  - Manifest.json returning 401 errors (blocked PWA features)
  - Service worker couldn't load (401 errors)
  - Home page media queries misaligned with other pages
  - Desktop-first CSS causing mobile overflow
- **Solution:**
  - Added Flask routes for `/manifest.json` and `/service-worker.js`
  - Updated base.html to use root-level paths
  - Fixed home page media queries (767px breakpoint, 60px padding)
  - Aligned mobile styles with dashboard/events/archive pages
- **Status:** ✅ Fixed - Tested in incognito mode, works perfectly across all pages

**Resolved Issues:**
- ✅ iOS install prompt - Added "How to Install" button with step-by-step instructions (Jan 16, 2026)
- ✅ Microsoft 365 authentication - Implemented (Jan 16, 2026)

**Phase 2 (Future Enhancements):**
- Push notifications (event summaries, weekly reminders)
- Real-time updates via Supabase subscriptions

---

### Maintenance & Update System (Subproject)
**Status:** ✅ COMPLETE & DEPLOYED (Jan 16, 2026)
**Goal:** Control app availability and silently push updates to users

**Features:**
- **Maintenance Mode:** Full lockout - redirect all users to maintenance page
- **Silent Auto-Updates:** Automatic cache clearing and reload when new version detected (no user prompt)
- **Admin Control Panel:** Mobile-friendly admin page to toggle settings
- **Version Tracking:** `/api/version` endpoint for debugging

**Admin Control Panel:**
- **URL:** `https://pianabihub.vercel.app/admin` (click "Admin" in desktop nav)
- **Access:** Password login (session-based, stays logged in 31 days)
- **Visibility:** Desktop navigation only (hidden from mobile menu)
- **Features:**
  - Toggle maintenance mode on/off
  - Set custom maintenance message
  - Update app version (triggers silent auto-update for all users)
  - Health status indicator (Supabase connection)
  - Quick links to Supabase and Vercel dashboards
  - Logout button

**How It Works:**

1. **Maintenance Mode**
   - Toggle via Admin Control Panel or Supabase `app_config` table
   - When `maintenance_mode.enabled = true`, all routes redirect to `/maintenance`
   - Maintenance page has "Admin Login" link at bottom for easy access
   - Maintenance page auto-polls every 30 seconds to check when back online

2. **Silent Auto-Updates**
   - Version stored in Supabase: `app_version.version` and `app_version.min_version`
   - On page load and when app becomes visible, JavaScript checks `/api/version`
   - If local version < `min_version`, silently clears cache and reloads (like Clash Royale updates)
   - No user prompt - happens automatically in background
   - Prevents infinite reload loops with sessionStorage flag

**How to Enable Maintenance Mode:**
1. Go to `https://pianabihub.vercel.app/admin` (or click "Admin" in desktop nav)
2. Enter password to login
3. Toggle the Maintenance Mode switch to ON
4. Optionally add a custom message
5. Click Enable/Update → App immediately shows maintenance page to all users
6. To disable: Toggle switch back to OFF

**How to Push an Update:**
1. Deploy new code to Vercel (push to GitHub)
2. Go to Admin Control Panel and login
3. Under "App Version", enter new version (e.g., `1.1.0`)
4. Click "Deploy Version Update"
5. All users silently get updated on their next visit (no prompt needed)

**Supabase Tables:**
- `app_config` - Stores `maintenance_mode` and `app_version` as JSONB

**Files Created/Modified (Jan 16, 2026):**
- `main.py` - Added `/admin` route, `get_app_config()`, `update_app_config()`, maintenance middleware
- `templates/admin.html` - Admin control panel (mobile-friendly)
- `static/service-worker.js` - Added message handler for `FORCE_UPDATE` cache clearing
- `templates/base.html` - Silent auto-update JavaScript (version checking, cache clearing)
- `templates/maintenance.html` - Maintenance page with auto-polling

**Troubleshooting:**
- If admin page returns 403, check that `ADMIN_SECRET` env var in Vercel doesn't have trailing newline
- To fix: Vercel Dashboard → Settings → Environment Variables → Delete and re-add ADMIN_SECRET

---

### Microsoft 365 Authentication (Subproject)
**Status:** ✅ COMPLETE & DEPLOYED (Jan 16, 2026)
**Goal:** Secure app with Microsoft 365 login, restrict to Tintoria-Piana employees

**Features:**
- **Microsoft Sign-In:** OAuth2 flow with Azure AD
- **Guest Access:** "Continue as Guest" option for quick access
- **Login Page:** Dedicated `/login` page with both options
- **User Dropdown:** Name in nav with dropdown showing email + sign out
- **Session Management:** Persistent login (stays logged in)

**How It Works:**
1. User visits any protected page → Redirected to `/login`
2. User chooses "Sign in with Microsoft" or "Continue as Guest"
3. Microsoft login: Redirects to Microsoft, then back with user info
4. Guest login: Creates guest session immediately
5. User sees their name in nav with dropdown for sign out

**Azure AD Setup (Already Done):**
- App registered in Azure AD portal
- Redirect URI: `https://pianabihub.vercel.app/callback`
- Permissions: `User.Read` (basic profile)
- Single tenant (Tintoria-Piana only)

**Environment Variables (Vercel):**
- `AZURE_CLIENT_ID` - Application (Client) ID from Azure
- `AZURE_TENANT_ID` - Directory (Tenant) ID from Azure
- `AZURE_CLIENT_SECRET` - Client secret value

**Routes:**
- `/login` - Login page with Microsoft + Guest options
- `/auth/microsoft` - Initiates Microsoft OAuth flow
- `/guest` - Creates guest session
- `/callback` - Handles Microsoft OAuth callback
- `/logout` - Clears session, redirects to Microsoft logout

**Technical Notes:**
- Uses manual OAuth2 flow with `requests` library (MSAL didn't work on Vercel)
- Fetches user info from Microsoft Graph API
- Admin link moved from nav to bottom of homepage (desktop only)

**Debug Endpoint:**
- `/api/auth-status` - Shows auth configuration status

**Files Modified (Jan 16, 2026):**
- `main.py` - OAuth2 routes, middleware, user session management
- `templates/login.html` - New login page
- `templates/base.html` - User dropdown, mobile menu updates
- `static/css/components.css` - Dropdown styles

---

### PWA Install Button (Subproject)
**Status:** ✅ COMPLETE & DEPLOYED (Jan 16, 2026)
**Goal:** Fix iOS install prompt, optimize for both platforms

**Features:**
- **iOS:** "How to Install" button shows step-by-step instructions (Share → Add to Home Screen)
- **Android:** Native install prompt via `beforeinstallprompt` event
- **Smart Detection:** Automatically detects platform and shows appropriate UI

**Files Modified:**
- `templates/base.html` - iOS detection, step-by-step instructions UI

---

### Security Improvements (Jan 16, 2026)
**Status:** ✅ COMPLETE

**Completed:**
- [x] Enabled RLS on all Supabase tables
- [x] No public policies = anon key blocked from direct access
- [x] Flask uses service role key for full server-side access
- [x] No client-side Supabase calls (key never exposed)
- [x] Microsoft 365 authentication for user access control

**Supabase RLS Status:**
| Table | RLS | Policies |
|-------|-----|----------|
| `app_config` | ✅ | Read: public, Write: blocked |
| `events` | ✅ | None (service role only) |
| `event_summaries` | ✅ | None (service role only) |
| `intelligence_reports` | ✅ | None (service role only) |
| `industry_events` | ✅ | None (service role only) |

---

### Session Notes (Jan 17, 2026)
- Investigated intermittent 404 error on guest login - likely caused by Vercel deployment in progress
- Set up two-branch deployment workflow (`develop` → `main`) for safer deployments
- Mobile PWA still on older version - will push version update when ready (not during weekend)

### Upcoming Tasks (Monday)
- [ ] Test making GitHub repo private (check if Vercel auto-deploy still works)
- [ ] Deploy version update to force mobile PWA refresh
- [ ] Fix event automation flow issue (Make.com)
- [ ] Fix login page and user dropdown visual styling (alignment, mobile optimization)
- [ ] Add "Stay signed in" checkbox on login page
- [ ] Upload 2026 Q2 events (April-June) when dates available
- [ ] Monitor Make.com automation for Q1 2026 event summaries
- [ ] Push notifications (future enhancement)
- [ ] Real-time updates via Supabase subscriptions (future enhancement)

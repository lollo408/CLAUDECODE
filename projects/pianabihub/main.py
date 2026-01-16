import os
import json
import ast
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from datetime import date, datetime
import csv
import io
from supabase import create_client, Client
from services.perplexity_service import generate_event_summary

# Try to import msal, but don't crash if it fails
try:
    import msal
    MSAL_AVAILABLE = True
except ImportError as e:
    print(f"[Auth] MSAL import failed: {e}")
    MSAL_AVAILABLE = False
    msal = None

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')


@app.context_processor
def inject_user():
    """Make user info available in all templates."""
    return {
        'current_user': session.get('user', None),
        'auth_enabled': all([
            os.environ.get('AZURE_CLIENT_ID'),
            os.environ.get('AZURE_CLIENT_SECRET'),
            os.environ.get('AZURE_TENANT_ID')
        ])
    }


# --- MICROSOFT AZURE AD CONFIGURATION ---
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
AZURE_AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}" if AZURE_TENANT_ID else None
AZURE_REDIRECT_PATH = "/callback"
AZURE_SCOPE = ["User.Read"]  # Basic profile info

# Check if Azure AD is configured AND msal is available
AZURE_AUTH_ENABLED = MSAL_AVAILABLE and all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID])

if AZURE_AUTH_ENABLED:
    print(f"[Auth] Azure AD authentication enabled")
else:
    print(f"[Auth] Azure AD authentication disabled (MSAL: {MSAL_AVAILABLE}, Client: {bool(AZURE_CLIENT_ID)}, Tenant: {bool(AZURE_TENANT_ID)}, Secret: {bool(AZURE_CLIENT_SECRET)})")


def get_msal_app():
    """Create MSAL confidential client application."""
    if not AZURE_AUTH_ENABLED or not msal:
        return None
    try:
        return msal.ConfidentialClientApplication(
            AZURE_CLIENT_ID,
            authority=AZURE_AUTHORITY,
            client_credential=AZURE_CLIENT_SECRET
        )
    except Exception as e:
        print(f"[Auth] Failed to create MSAL app: {e}")
        return None


def get_auth_url():
    """Generate Microsoft login URL."""
    msal_app = get_msal_app()
    if not msal_app:
        return None

    # Build redirect URI from request
    redirect_uri = request.url_root.rstrip('/') + AZURE_REDIRECT_PATH

    auth_url = msal_app.get_authorization_request_url(
        scopes=AZURE_SCOPE,
        redirect_uri=redirect_uri,
        state=request.args.get('next', '/')
    )
    return auth_url


def is_user_authenticated():
    """Check if current user is authenticated."""
    if not AZURE_AUTH_ENABLED:
        return True  # If auth not configured, allow access
    return 'user' in session


def get_current_user():
    """Get current user info from session."""
    return session.get('user', None)


url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError(
        f"Missing Supabase credentials! URL: {bool(url)}, KEY: {bool(key)}")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise ValueError(f"Failed to create Supabase client. Error: {e}")


# --- APP CONFIG HELPER FUNCTIONS ---
def get_app_config(key):
    """Fetches a config value from app_config table."""
    try:
        response = supabase.table('app_config') \
            .select('value') \
            .eq('key', key) \
            .limit(1) \
            .execute()
        return response.data[0]['value'] if response.data else None
    except Exception as e:
        print(f"Error fetching app config {key}: {e}")
        return None


def update_app_config(key, value):
    """Updates a config value in app_config table."""
    try:
        response = supabase.table('app_config') \
            .update({'value': value}) \
            .eq('key', key) \
            .execute()
        return True
    except Exception as e:
        print(f"Error updating app config {key}: {e}")
        return False


# --- AUTHENTICATION & MAINTENANCE MIDDLEWARE ---
@app.before_request
def check_auth_and_maintenance():
    """Check authentication and maintenance mode before every request."""
    # Paths that don't require auth or maintenance check
    public_paths = [
        '/login',
        '/callback',
        '/logout',
        '/maintenance',
        '/static/',
        '/api/version',
        '/manifest.json',
        '/service-worker.js',
        '/offline'
    ]

    # Check if current path is public
    for path in public_paths:
        if request.path.startswith(path):
            return None

    # Admin paths have their own auth
    if request.path.startswith('/admin'):
        return None

    # Check authentication (if Azure AD is enabled)
    if AZURE_AUTH_ENABLED and not is_user_authenticated():
        # Store the intended destination
        session['next_url'] = request.url
        return redirect(url_for('login'))

    # Admin bypass for maintenance: ?admin_key=secret
    admin_secret = os.environ.get('ADMIN_SECRET', 'piana2026')
    if request.args.get('admin_key') == admin_secret:
        return None

    # Check maintenance mode from Supabase
    maintenance_config = get_app_config('maintenance_mode')
    if maintenance_config and maintenance_config.get('enabled'):
        return redirect(url_for('maintenance'))

    return None


# --- AUTHENTICATION ROUTES ---
@app.route('/login')
def login():
    """Redirect to Microsoft login page."""
    if not AZURE_AUTH_ENABLED:
        return redirect(url_for('home'))

    auth_url = get_auth_url()
    if auth_url:
        return redirect(auth_url)
    return "Authentication not configured", 500


@app.route('/callback')
def callback():
    """Handle the callback from Microsoft after login."""
    if not AZURE_AUTH_ENABLED:
        return redirect(url_for('home'))

    # Check for errors
    if 'error' in request.args:
        error_desc = request.args.get('error_description', 'Unknown error')
        return f"Login failed: {error_desc}", 400

    # Get the authorization code
    code = request.args.get('code')
    if not code:
        return "No authorization code received", 400

    # Build redirect URI (must match what was used in auth request)
    redirect_uri = request.url_root.rstrip('/') + AZURE_REDIRECT_PATH

    # Exchange code for tokens
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=AZURE_SCOPE,
        redirect_uri=redirect_uri
    )

    if 'error' in result:
        return f"Token error: {result.get('error_description', result.get('error'))}", 400

    # Store user info in session
    if 'id_token_claims' in result:
        session['user'] = {
            'name': result['id_token_claims'].get('name', 'User'),
            'email': result['id_token_claims'].get('preferred_username', ''),
            'oid': result['id_token_claims'].get('oid', '')
        }
        session.permanent = True

    # Redirect to original destination or home
    next_url = request.args.get('state', '/') or session.pop('next_url', '/')
    return redirect(next_url)


@app.route('/logout')
def logout():
    """Log out the user."""
    session.clear()

    if AZURE_AUTH_ENABLED:
        # Redirect to Microsoft logout
        logout_url = f"{AZURE_AUTHORITY}/oauth2/v2.0/logout?post_logout_redirect_uri={request.url_root}"
        return redirect(logout_url)

    return redirect(url_for('home'))


# --- HELPER FUNCTION: Fetch & Clean Data ---
def get_latest_report(vertical_name):
    """Fetches and cleans the latest report for a given vertical."""
    try:
        response = supabase.table('intelligence_reports') \
            .select("*") \
            .eq('vertical', vertical_name) \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        data = response.data[0] if response.data else None

        if data and isinstance(data, dict):
            # --- ROBUST JSON CLEANING ---
            top_3 = data.get('top_3_json')
            if isinstance(top_3, str):
                # NEW: Strip Markdown code blocks if they exist
                top_3 = top_3.replace('```json', '').replace('```', '').strip()

                try:
                    # Attempt 1: Standard JSON
                    data['top_3_json'] = json.loads(top_3)
                except json.JSONDecodeError:
                    try:
                        # Attempt 2: Python Literal
                        data['top_3_json'] = ast.literal_eval(top_3)
                        print(f"✅ Parsed {vertical_name} using AST")
                    except Exception as e:
                        print(
                            f"❌ Failed to parse JSON for {vertical_name}: {e}")
                        data['top_3_json'] = []

            # Clean HTML
            report_html = data.get('report_html')
            if isinstance(report_html, str):
                data['report_html'] = report_html.replace('\\n',
                                                          '\n').strip('"')

        return data
    except Exception as e:
        print(f"Error fetching {vertical_name}: {e}")
        return None


# --- EVENTS HELPER FUNCTIONS ---
def get_all_events(filter_type='3months', industry=None):
    """Fetches events with optional filtering."""
    try:
        from datetime import timedelta

        query = supabase.table('events').select("*")

        if industry and industry != 'all':
            query = query.eq('industry', industry)

        today = date.today()

        if filter_type == '3months':
            # Next 3 months rolling window
            three_months_out = (today + timedelta(days=90)).isoformat()
            query = query.gte('start_date', today.isoformat()).lte('start_date', three_months_out)
        elif filter_type == 'upcoming':
            query = query.gte('start_date', today.isoformat())
        elif filter_type == 'past':
            query = query.lt('start_date', today.isoformat())
        # 'all' = no date filter

        response = query.order('start_date', desc=False).execute()
        return response.data
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []


def get_event_by_id(event_id):
    """Fetches a single event by ID."""
    try:
        response = supabase.table('events') \
            .select("*") \
            .eq('id', event_id) \
            .limit(1) \
            .execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error fetching event {event_id}: {e}")
        return None


# --- ROUTES ---


@app.route('/')
def home():
    """
    The Landing Page (Mission Control).
    """
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    """
    The Main Dashboard.
    Fetches reports for ALL 4 verticals.
    """
    # Fetch all 4 verticals
    hospitality = get_latest_report('hospitality')
    automotive = get_latest_report('automotive')
    bedding = get_latest_report('bedding')
    textiles = get_latest_report('textiles')

    # Render with all datasets
    return render_template('index.html',
                           hospitality_data=hospitality,
                           automotive_data=automotive,
                           bedding_data=bedding,
                           textiles_data=textiles)


@app.route('/archive')
def archive():
    """Archive page with search/filter capability."""
    try:
        from datetime import timedelta

        # Get filter parameters
        vertical = request.args.get('vertical', 'all')
        timeframe = request.args.get('timeframe', '3months')

        # Build query
        query = supabase.table('intelligence_reports').select("*")

        # Filter by vertical
        if vertical and vertical != 'all':
            query = query.eq('vertical', vertical.lower())

        # Filter by timeframe
        today = date.today()
        if timeframe == '1month':
            cutoff = (today - timedelta(days=30)).isoformat()
            query = query.gte('created_at', cutoff)
        elif timeframe == '3months':
            cutoff = (today - timedelta(days=90)).isoformat()
            query = query.gte('created_at', cutoff)
        # No 'all' option - only 1 month or 3 months

        # Order and limit results (max 8)
        response = query.order('created_at', desc=True).limit(8).execute()

        return render_template('archive.html',
                             reports=response.data,
                             current_vertical=vertical,
                             current_timeframe=timeframe)
    except Exception as e:
        return f"<h3>Archive Error: {e}</h3>", 500


# --- EVENTS ROUTES ---

@app.route('/events')
def events():
    """Events listing page with filters, upcoming notifications, and pagination."""
    filter_type = request.args.get('filter', '3months')
    industry = request.args.get('industry', 'all')
    page = int(request.args.get('page', 1))

    # Pagination settings
    per_page = 8
    offset = (page - 1) * per_page

    # Get all events (for count and upcoming section)
    all_events = get_all_events(filter_type, industry)
    today = date.today()

    # Process events for display
    upcoming_events = []
    for event in all_events:
        if not event:
            continue
        try:
            start_date = datetime.strptime(event['start_date'], '%Y-%m-%d').date()
            end_date_str = event.get('end_date') or event['start_date']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            days_until = (start_date - today).days
            event['days_until'] = days_until
            event['is_upcoming'] = 0 < days_until <= 14
            event['is_past'] = end_date < today
            event['is_this_week'] = 0 < days_until <= 7

            # Collect upcoming for featured section
            if 0 < days_until <= 14:
                upcoming_events.append(event)
        except Exception:
            event['days_until'] = None
            event['is_upcoming'] = False
            event['is_past'] = False
            event['is_this_week'] = False

    # Sort upcoming by soonest first
    upcoming_events.sort(key=lambda x: x.get('days_until', 999))

    # Paginate main events list
    total_events = len(all_events)
    total_pages = (total_events + per_page - 1) // per_page  # Ceiling division
    events_list = all_events[offset:offset + per_page]

    return render_template('events.html',
                           events=events_list,
                           upcoming_events=upcoming_events,
                           current_filter=filter_type,
                           current_industry=industry,
                           current_page=page,
                           total_pages=total_pages,
                           has_next=page < total_pages,
                           has_prev=page > 1)


@app.route('/events/<event_id>')
def event_detail(event_id):
    """Single event detail page with AI summary."""
    event = get_event_by_id(event_id)
    if not event:
        return "<h3>Event not found</h3>", 404

    # Fetch summary if exists
    summary = None
    try:
        summary_response = supabase.table('event_summaries') \
            .select('*') \
            .eq('event_id', event_id) \
            .eq('status', 'completed') \
            .limit(1) \
            .execute()
        summary = summary_response.data[0] if summary_response.data else None
    except Exception as e:
        print(f"Error fetching summary: {e}")

    # Determine if event is past
    end_date_str = event.get('end_date') or event.get('start_date')
    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        is_past_event = end_date < date.today()
    except:
        is_past_event = False

    return render_template('event_detail.html',
                           event=event,
                           summary=summary,
                           is_past_event=is_past_event)


@app.route('/upload-events', methods=['GET', 'POST'])
def upload_events():
    """CSV upload for events - Admin only."""
    # Admin protection: require ?key=<admin_secret>
    admin_secret = os.environ.get('ADMIN_SECRET', 'piana2026')
    if request.args.get('key') != admin_secret:
        return "<h3>Unauthorized - Admin access required</h3>", 403

    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('upload_events.html', error="No file selected")

        file = request.files['file']
        if not file.filename or file.filename == '':
            return render_template('upload_events.html', error="No file selected")

        if not file.filename.endswith('.csv'):
            return render_template('upload_events.html', error="Please upload a CSV file")

        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            reader = csv.DictReader(stream)

            count = 0
            skipped = 0
            for row in reader:
                event_data = {
                    'name': row.get('name', '').strip(),
                    'industry': row.get('industry', '').strip() or None,
                    'start_date': row.get('start_date', '').strip(),
                    'end_date': row.get('end_date', '').strip() or None,
                    'location': row.get('location', '').strip() or None,
                    'country': row.get('country', '').strip() or None,
                    'website': row.get('website', '').strip() or None,
                    'description': row.get('description', '').strip() or None,
                }

                if event_data['name'] and event_data['start_date']:
                    # Check for duplicates
                    existing = supabase.table('events') \
                        .select('id') \
                        .eq('name', event_data['name']) \
                        .eq('start_date', event_data['start_date']) \
                        .execute()

                    if existing.data:
                        skipped += 1
                        continue

                    supabase.table('events').insert(event_data).execute()
                    count += 1

            return redirect(url_for('events') + f'?uploaded={count}&skipped={skipped}')

        except Exception as e:
            return render_template('upload_events.html', error=f"Error processing file: {e}")

    return render_template('upload_events.html')


@app.route('/offline')
def offline():
    """Offline fallback page for PWA"""
    return render_template('offline.html')


@app.route('/maintenance')
def maintenance():
    """Maintenance mode page - shown when app is under maintenance."""
    maintenance_config = get_app_config('maintenance_mode')
    message = ""
    if maintenance_config:
        message = maintenance_config.get('message', '')
    return render_template('maintenance.html', message=message)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin control panel for app management."""
    admin_secret = os.environ.get('ADMIN_SECRET', 'piana2026')

    # Check if already authenticated via session or URL key (for backwards compatibility)
    is_authenticated = session.get('admin_authenticated') or request.args.get('key') == admin_secret

    message = None
    error = None

    # Handle login attempt
    if request.method == 'POST' and request.form.get('action') == 'login':
        password = request.form.get('password', '')
        if password == admin_secret:
            session['admin_authenticated'] = True
            session.permanent = True  # Keep session for 31 days
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html',
                                   authenticated=False,
                                   login_error="Invalid password")

    # If not authenticated, show login form
    if not is_authenticated:
        return render_template('admin.html', authenticated=False)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'toggle_maintenance':
            enabled = request.form.get('enabled') == 'true'
            maint_message = request.form.get('message', '')
            success = update_app_config('maintenance_mode', {
                'enabled': enabled,
                'message': maint_message
            })
            if success:
                message = f"Maintenance mode {'enabled' if enabled else 'disabled'}"
            else:
                error = "Failed to update maintenance mode"

        elif action == 'update_version':
            new_version = request.form.get('version', '').strip()
            if new_version:
                current = get_app_config('app_version') or {}
                success = update_app_config('app_version', {
                    'version': new_version,
                    'min_version': new_version  # Force update for all users
                })
                if success:
                    message = f"Version updated to {new_version} - users will auto-update"
                else:
                    error = "Failed to update version"
            else:
                error = "Version cannot be empty"

    # Get current config
    maintenance_config = get_app_config('maintenance_mode') or {'enabled': False, 'message': ''}
    version_config = get_app_config('app_version') or {'version': '1.0.0', 'min_version': '1.0.0'}

    # Health check
    health = {'supabase': False, 'status': 'unknown'}
    try:
        test = supabase.table('app_config').select('key').limit(1).execute()
        health['supabase'] = True
        health['status'] = 'healthy'
    except:
        health['status'] = 'database error'

    return render_template('admin.html',
                           authenticated=True,
                           maintenance=maintenance_config,
                           version=version_config,
                           health=health,
                           message=message,
                           error=error)


@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel."""
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))


@app.route('/api/version')
def api_version():
    """Returns app version info for service worker update checks."""
    version_config = get_app_config('app_version')
    if version_config:
        return jsonify({
            'version': version_config.get('version', '1.0.0'),
            'min_version': version_config.get('min_version', '1.0.0')
        })
    # Default if config not found
    return jsonify({
        'version': '1.0.0',
        'min_version': '1.0.0'
    })


@app.route('/manifest.json')
def manifest():
    """Serve PWA manifest file"""
    from flask import send_from_directory
    return send_from_directory('static', 'manifest.json', mimetype='application/manifest+json')


@app.route('/service-worker.js')
def service_worker():
    """Serve service worker file"""
    from flask import send_from_directory
    return send_from_directory('static', 'service-worker.js', mimetype='application/javascript')


# --- API ENDPOINTS ---

@app.route('/api/generate-summary', methods=['POST'])
def api_generate_summary():
    """
    Webhook endpoint for Make.com to trigger summary generation.

    Expected JSON payload:
    {
        "event_id": "uuid-here",
        "webhook_secret": "your-secret"
    }
    """
    webhook_secret = os.environ.get('WEBHOOK_SECRET', 'make-webhook-2026')

    data = request.get_json()

    # Validate webhook secret
    if data.get('webhook_secret') != webhook_secret:
        return jsonify({'error': 'Unauthorized'}), 401

    event_id = data.get('event_id')
    if not event_id:
        return jsonify({'error': 'event_id required'}), 400

    # Fetch event from Supabase
    try:
        event_response = supabase.table('events').select('*').eq('id', event_id).single().execute()
        event = event_response.data
    except Exception as e:
        return jsonify({'error': f'Event not found: {e}'}), 404

    if not event:
        return jsonify({'error': 'Event not found'}), 404

    # Generate summary via Perplexity
    result = generate_event_summary(
        event_name=event['name'],
        event_date=event.get('end_date') or event['start_date'],
        industry=event.get('industry', 'General'),
        location=event.get('location', 'Unknown'),
        website=event.get('website')
    )

    if result['success']:
        # Save to event_summaries table
        try:
            supabase.table('event_summaries').insert({
                'event_id': event_id,
                'summary_text': result['summary'],
                'status': 'completed'
            }).execute()

            return jsonify({'success': True, 'summary': result['summary']})
        except Exception as e:
            return jsonify({'error': f'Failed to save summary: {e}'}), 500
    else:
        # Log failure
        try:
            supabase.table('event_summaries').insert({
                'event_id': event_id,
                'summary_text': '',
                'status': 'failed'
            }).execute()
        except:
            pass

        return jsonify({'success': False, 'error': result['error']}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

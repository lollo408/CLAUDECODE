import os
import json
import ast
import string
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, make_response
from datetime import date, datetime
import csv
import io
from supabase import create_client, Client
from services.perplexity_service import generate_event_summary
from werkzeug.security import generate_password_hash, check_password_hash

import requests as http_requests  # Rename to avoid confusion with flask.request
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')


@app.context_processor
def inject_user():
    """Make user info available in all templates."""
    # Check maintenance status for admin indicator
    is_admin = session.get('admin_authenticated', False)
    maintenance_active = False
    if is_admin:
        try:
            maint_config = get_app_config('maintenance_mode')
            maintenance_active = maint_config.get('enabled', False) if maint_config else False
        except:
            pass

    user = session.get('user', None)
    user_type = None
    if user:
        if user.get('is_guest'):
            user_type = 'guest'
        elif user.get('user_type') == 'partner':
            user_type = 'partner'
        else:
            user_type = 'employee'

    return {
        'current_user': user,
        'user_type': user_type,
        'is_admin': is_admin,
        'maintenance_active': maintenance_active,
        'auth_enabled': all([
            os.environ.get('AZURE_CLIENT_ID'),
            os.environ.get('AZURE_CLIENT_SECRET'),
            os.environ.get('AZURE_TENANT_ID')
        ])
    }


# --- MICROSOFT AZURE AD CONFIGURATION (Manual OAuth2) ---
AZURE_CLIENT_ID = os.environ.get('AZURE_CLIENT_ID')
AZURE_CLIENT_SECRET = os.environ.get('AZURE_CLIENT_SECRET')
AZURE_TENANT_ID = os.environ.get('AZURE_TENANT_ID')
AZURE_REDIRECT_PATH = "/callback"
AZURE_SCOPE = "openid profile email User.Read"

# Azure OAuth2 endpoints
AZURE_AUTH_ENDPOINT = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/authorize" if AZURE_TENANT_ID else None
AZURE_TOKEN_ENDPOINT = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token" if AZURE_TENANT_ID else None
AZURE_LOGOUT_ENDPOINT = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/logout" if AZURE_TENANT_ID else None

# Check if Azure AD is configured
AZURE_AUTH_ENABLED = all([AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID])

if AZURE_AUTH_ENABLED:
    print(f"[Auth] Azure AD authentication enabled (manual OAuth2)")
else:
    print(f"[Auth] Azure AD authentication disabled (Client: {bool(AZURE_CLIENT_ID)}, Tenant: {bool(AZURE_TENANT_ID)}, Secret: {bool(AZURE_CLIENT_SECRET)})")


def get_auth_url(redirect_uri, state=None):
    """Generate Microsoft OAuth2 authorization URL."""
    if not AZURE_AUTH_ENABLED:
        return None

    # Generate a random state for CSRF protection if not provided
    if not state:
        state = secrets.token_urlsafe(32)

    params = {
        'client_id': AZURE_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': AZURE_SCOPE,
        'response_mode': 'query',
        'state': state,
        'prompt': 'select_account'  # Always show account picker
    }

    query_string = '&'.join(f"{k}={v}" for k, v in params.items())
    return f"{AZURE_AUTH_ENDPOINT}?{query_string}"


def exchange_code_for_tokens(code, redirect_uri):
    """Exchange authorization code for tokens."""
    if not AZURE_AUTH_ENABLED:
        return None

    data = {
        'client_id': AZURE_CLIENT_ID,
        'client_secret': AZURE_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'scope': AZURE_SCOPE
    }

    try:
        response = http_requests.post(AZURE_TOKEN_ENDPOINT, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Auth] Token exchange failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[Auth] Token exchange error: {e}")
        return None


def get_user_info(access_token):
    """Get user info from Microsoft Graph API."""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = http_requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Auth] User info fetch failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"[Auth] User info error: {e}")
        return None


def is_user_authenticated():
    """Check if current user is authenticated (Microsoft or Guest)."""
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


# --- USER PREFERENCES HELPER FUNCTIONS ---
def get_user_preferences(user):
    """
    Fetches user preferences.
    - Microsoft users: from Supabase user_preferences table
    - Guest users: from session
    Returns dict with preferred_industry, notifications_enabled
    """
    if not user:
        return {'preferred_industry': None, 'notifications_enabled': True}

    # Guest users: use session storage
    if user.get('is_guest'):
        return session.get('user_preferences', {
            'preferred_industry': None,
            'notifications_enabled': True
        })

    # Microsoft users: fetch from database
    user_id = user.get('id')
    if not user_id:
        return {'preferred_industry': None, 'notifications_enabled': True}

    try:
        response = supabase.table('user_preferences') \
            .select('*') \
            .eq('user_id', user_id) \
            .limit(1) \
            .execute()

        if response.data:
            prefs = response.data[0]
            return {
                'preferred_industry': prefs.get('preferred_industry'),
                'notifications_enabled': prefs.get('notifications_enabled', True)
            }
        return {'preferred_industry': None, 'notifications_enabled': True}
    except Exception as e:
        print(f"Error fetching user preferences: {e}")
        return {'preferred_industry': None, 'notifications_enabled': True}


def save_user_preferences(user, prefs):
    """
    Saves user preferences.
    - Microsoft users: to Supabase user_preferences table
    - Guest users: to session
    Returns True on success, False on failure.
    """
    if not user:
        return False

    # Guest users: save to session
    if user.get('is_guest'):
        session['user_preferences'] = prefs
        return True

    # Microsoft users and Partners: upsert to database
    user_id = user.get('id')
    if not user_id:
        return False

    try:
        # Upsert: insert or update if exists
        response = supabase.table('user_preferences') \
            .upsert({
                'user_id': user_id,
                'preferred_industry': prefs.get('preferred_industry'),
                'notifications_enabled': prefs.get('notifications_enabled', True),
                'updated_at': datetime.now().isoformat()
            }, on_conflict='user_id') \
            .execute()
        return True
    except Exception as e:
        print(f"Error saving user preferences: {e}")
        return False


# --- PARTNER AUTHENTICATION HELPER FUNCTIONS ---
def generate_invite_code(length=8):
    """Generate a random invite code (uppercase letters and digits)."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def validate_invite_code(code):
    """
    Check if an invite code is valid (exists, not used, not expired).
    Returns the invite record if valid, None otherwise.
    """
    if not code:
        return None

    try:
        response = supabase.table('invite_codes') \
            .select('*') \
            .eq('code', code.upper()) \
            .is_('used_by', 'null') \
            .limit(1) \
            .execute()

        if not response.data:
            return None

        invite = response.data[0]

        # Check expiration if set
        if invite.get('expires_at'):
            expires = datetime.fromisoformat(invite['expires_at'].replace('Z', '+00:00'))
            if datetime.now(expires.tzinfo) > expires:
                return None

        return invite
    except Exception as e:
        print(f"Error validating invite code: {e}")
        return None


def create_partner_user(email, password, company_name, invite_code):
    """
    Create a new partner user account.
    Returns (user_dict, error_message) tuple.
    """
    email = email.lower().strip()

    # Check if email already exists
    try:
        existing = supabase.table('partner_users') \
            .select('id') \
            .eq('email', email) \
            .limit(1) \
            .execute()

        if existing.data:
            return None, "An account with this email already exists"
    except Exception as e:
        print(f"Error checking existing user: {e}")
        return None, "Registration failed. Please try again."

    # Create the user
    try:
        password_hash = generate_password_hash(password)

        response = supabase.table('partner_users') \
            .insert({
                'email': email,
                'password_hash': password_hash,
                'company_name': company_name.strip()
            }) \
            .execute()

        if not response.data:
            return None, "Registration failed. Please try again."

        new_user = response.data[0]

        # Mark invite code as used
        supabase.table('invite_codes') \
            .update({
                'used_by': new_user['id'],
                'used_at': datetime.now().isoformat()
            }) \
            .eq('code', invite_code.upper()) \
            .execute()

        return new_user, None

    except Exception as e:
        print(f"Error creating partner user: {e}")
        return None, "Registration failed. Please try again."


def authenticate_partner(email, password):
    """
    Authenticate a partner user with email and password.
    Returns (user_dict, error_message) tuple.
    """
    email = email.lower().strip()

    try:
        response = supabase.table('partner_users') \
            .select('*') \
            .eq('email', email) \
            .eq('is_active', True) \
            .limit(1) \
            .execute()

        if not response.data:
            return None, "Invalid email or password"

        user = response.data[0]

        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return None, "Invalid email or password"

        # Update last login
        supabase.table('partner_users') \
            .update({'last_login': datetime.now().isoformat()}) \
            .eq('id', user['id']) \
            .execute()

        return user, None

    except Exception as e:
        print(f"Error authenticating partner: {e}")
        return None, "Login failed. Please try again."


def get_user_type(user):
    """
    Returns the user type: 'guest', 'partner', or 'employee'.
    """
    if not user:
        return None
    if user.get('is_guest'):
        return 'guest'
    if user.get('user_type') == 'partner':
        return 'partner'
    # Microsoft users (have 'id' from Azure AD)
    return 'employee'


# --- AUTHENTICATION & MAINTENANCE MIDDLEWARE ---
@app.before_request
def check_auth_and_maintenance():
    """Check authentication and maintenance mode before every request."""
    # Paths that don't require auth or maintenance check
    public_paths = [
        '/login',
        '/register',
        '/auth/',
        '/guest',
        '/callback',
        '/logout',
        '/maintenance',
        '/static/',
        '/api/version',
        '/api/auth-status',
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

    # Always require login (user must be in session - either Microsoft or Guest)
    if not is_user_authenticated():
        # Only store actual page paths as next_url (not assets like favicon.ico)
        # This prevents redirect issues when browser auto-requests favicon
        if not request.path.startswith('/favicon') and '.' not in request.path:
            session['next_url'] = request.path
        return redirect(url_for('login'))

    # Check maintenance mode from Supabase
    maintenance_config = get_app_config('maintenance_mode')
    if maintenance_config and maintenance_config.get('enabled'):
        # Admin bypass: if user is admin-authenticated, allow full site access
        if session.get('admin_authenticated'):
            return None
        return redirect(url_for('maintenance'))

    return None


# --- AUTHENTICATION ROUTES ---
@app.route('/login')
def login():
    """Show login page with options."""
    # If already logged in, go to home
    if is_user_authenticated():
        return redirect(url_for('home'))

    error = request.args.get('error')
    logged_out = request.args.get('logged_out') == 'true'
    return render_template('login.html',
                         auth_available=AZURE_AUTH_ENABLED,
                         error=error,
                         logged_out=logged_out)


@app.route('/auth/microsoft')
def auth_microsoft():
    """Redirect to Microsoft login page."""
    if not AZURE_AUTH_ENABLED:
        return redirect(url_for('login', error='Microsoft authentication not configured'))

    # Store remember preference for use after OAuth callback
    remember = request.args.get('remember', '1') == '1'
    session['remember_me'] = remember

    # Build redirect URI
    redirect_uri = request.url_root.rstrip('/') + AZURE_REDIRECT_PATH

    # Generate state and store in session for CSRF protection
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    auth_url = get_auth_url(redirect_uri, state)
    if auth_url:
        return redirect(auth_url)
    return redirect(url_for('login', error='Failed to generate login URL'))


@app.route('/guest')
def guest_login():
    """Allow guest access without Microsoft login."""
    remember = request.args.get('remember', '1') == '1'
    session['user'] = {
        'name': 'Guest',
        'email': 'guest@piana.com',
        'is_guest': True
    }
    session.permanent = remember

    # Get stored destination, default to home
    next_url = session.pop('next_url', None)
    if not next_url or next_url == '/login':
        next_url = '/'

    return redirect(next_url)


@app.route('/callback')
def callback():
    """Handle the callback from Microsoft after login."""
    if not AZURE_AUTH_ENABLED:
        return redirect(url_for('home'))

    # Check for errors
    if 'error' in request.args:
        error_desc = request.args.get('error_description', 'Unknown error')
        return redirect(url_for('login', error=error_desc))

    # Get the authorization code
    code = request.args.get('code')
    if not code:
        return redirect(url_for('login', error='No authorization code received'))

    # Build redirect URI (must match what was used in auth request)
    redirect_uri = request.url_root.rstrip('/') + AZURE_REDIRECT_PATH

    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code, redirect_uri)
    if not tokens:
        return redirect(url_for('login', error='Failed to authenticate with Microsoft'))

    # Get user info from Microsoft Graph
    access_token = tokens.get('access_token')
    if access_token:
        user_info = get_user_info(access_token)
        if user_info:
            session['user'] = {
                'name': user_info.get('displayName', 'User'),
                'email': user_info.get('mail') or user_info.get('userPrincipalName', ''),
                'id': user_info.get('id', '')
            }
            # Only set permanent session if user wants to stay signed in
            remember = session.pop('remember_me', True)
            session.permanent = remember
        else:
            return redirect(url_for('login', error='Failed to get user information'))
    else:
        return redirect(url_for('login', error='No access token received'))

    # Clear OAuth state
    session.pop('oauth_state', None)

    # Redirect to original destination or home
    next_url = session.pop('next_url', '/')
    return redirect(next_url)


@app.route('/logout')
def logout():
    """Log out the user."""
    was_microsoft_user = session.get('user', {}).get('id')  # Microsoft users have 'id'
    session.clear()

    # Always redirect to login page directly (faster, no double redirect)
    # Skip Microsoft's logout endpoint - it's slow and unnecessary for our use case
    # The session is already cleared, so the user is logged out on our side
    return redirect(url_for('login', logged_out='true'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Partner registration with invite code."""
    # If already logged in, go to home
    if is_user_authenticated():
        return redirect(url_for('home'))

    invite_code = request.args.get('invite', '').upper()
    error = None
    success = False

    # Validate invite code on GET
    invite = validate_invite_code(invite_code) if invite_code else None

    if request.method == 'POST':
        invite_code = request.form.get('invite_code', '').upper()
        email = request.form.get('email', '').strip()
        company_name = request.form.get('company_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Re-validate invite code
        invite = validate_invite_code(invite_code)

        if not invite:
            error = "Invalid or expired invite code"
        elif not email or '@' not in email:
            error = "Please enter a valid email address"
        elif not company_name:
            error = "Please enter your company name"
        elif len(password) < 8:
            error = "Password must be at least 8 characters"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            # Create the account
            user, err = create_partner_user(email, password, company_name, invite_code)
            if user:
                success = True
            else:
                error = err

    return render_template('register.html',
                           invite_code=invite_code,
                           invite=invite,
                           error=error,
                           success=success)


@app.route('/auth/partner', methods=['GET', 'POST'])
def auth_partner():
    """Partner login with email and password."""
    # If already logged in, go to home
    if is_user_authenticated():
        return redirect(url_for('home'))

    error = None

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            error = "Please enter your email and password"
        else:
            user, err = authenticate_partner(email, password)
            if user:
                # Set up session
                session['user'] = {
                    'id': user['id'],
                    'name': user['company_name'],
                    'email': user['email'],
                    'user_type': 'partner'
                }
                session.permanent = remember

                # Redirect to original destination or home
                next_url = session.pop('next_url', '/')
                return redirect(next_url)
            else:
                error = err

    return render_template('partner_login.html', error=error)


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


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    User settings page for personalization preferences.
    GET: Display current settings
    POST: Save updated settings
    """
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))

    message = None
    error = None

    if request.method == 'POST':
        # Get form values
        preferred_industry = request.form.get('preferred_industry', '').strip()
        notifications_enabled = request.form.get('notifications_enabled') == 'on'

        # Clean up empty strings to None
        if not preferred_industry:
            preferred_industry = None

        # Save preferences
        prefs = {
            'preferred_industry': preferred_industry,
            'notifications_enabled': notifications_enabled
        }

        if save_user_preferences(user, prefs):
            message = "Settings saved successfully"
        else:
            error = "Failed to save settings. Please try again."

    # Get current preferences
    current_prefs = get_user_preferences(user)

    return render_template('settings.html',
                           preferences=current_prefs,
                           message=message,
                           error=error,
                           is_guest=user.get('is_guest', False))


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

    # Get user's preferred industry for default tab
    user = get_current_user()
    prefs = get_user_preferences(user)
    default_industry = prefs.get('preferred_industry') or 'Hospitality'

    # Render with all datasets
    return render_template('index.html',
                           hospitality_data=hospitality,
                           automotive_data=automotive,
                           bedding_data=bedding,
                           textiles_data=textiles,
                           default_industry=default_industry)


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

    # Use user's preferred industry as default if no industry param in URL
    industry = request.args.get('industry')
    if industry is None:
        # No industry param in URL - check user preference
        user = get_current_user()
        prefs = get_user_preferences(user)
        industry = prefs.get('preferred_industry') or 'all'
    elif industry == '':
        industry = 'all'

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

        elif action == 'create_invite':
            company_name = request.form.get('company_name', '').strip()
            code = generate_invite_code()
            try:
                supabase.table('invite_codes').insert({
                    'code': code,
                    'company_name': company_name if company_name else None,
                    'created_by': 'admin'
                }).execute()
                # Store the full link for display
                base_url = request.url_root.rstrip('/')
                session['new_invite_link'] = f"{base_url}/register?invite={code}"
                message = "Invite link created successfully"
            except Exception as e:
                error = f"Failed to create invite code: {e}"

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

    # Get invite codes (recent 10, unused first)
    invite_codes = []
    try:
        response = supabase.table('invite_codes') \
            .select('*') \
            .order('created_at', desc=True) \
            .limit(10) \
            .execute()
        invite_codes = response.data or []
    except Exception as e:
        print(f"Error fetching invite codes: {e}")

    # Get partner stats
    partner_stats = {'total': 0, 'active': 0}
    try:
        response = supabase.table('partner_users').select('id, is_active').execute()
        if response.data:
            partner_stats['total'] = len(response.data)
            partner_stats['active'] = sum(1 for p in response.data if p.get('is_active', True))
    except Exception as e:
        print(f"Error fetching partner stats: {e}")

    # Build base URL for invite links
    base_url = request.url_root.rstrip('/')

    # Get newly created invite link (if any) and clear from session
    new_invite_link = session.pop('new_invite_link', None)

    return render_template('admin.html',
                           authenticated=True,
                           maintenance=maintenance_config,
                           version=version_config,
                           health=health,
                           invite_codes=invite_codes,
                           partner_stats=partner_stats,
                           base_url=base_url,
                           new_invite_link=new_invite_link,
                           message=message,
                           error=error)


@app.route('/admin/logout')
def admin_logout():
    """Logout from admin panel."""
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))


@app.route('/api/auth-status')
def api_auth_status():
    """Debug endpoint to check auth configuration."""
    return jsonify({
        'auth_method': 'manual_oauth2',
        'azure_auth_enabled': AZURE_AUTH_ENABLED,
        'has_client_id': bool(AZURE_CLIENT_ID),
        'has_tenant_id': bool(AZURE_TENANT_ID),
        'has_client_secret': bool(AZURE_CLIENT_SECRET),
        'client_id_preview': AZURE_CLIENT_ID[:8] + '...' if AZURE_CLIENT_ID else None
    })


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

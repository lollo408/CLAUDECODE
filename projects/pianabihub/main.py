import os
import json
import ast  # <--- NEW: Add this library
from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import date, datetime
import csv
import io
from supabase import create_client, Client
from services.perplexity_service import generate_event_summary

app = Flask(__name__)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError(
        f"Missing Supabase credentials! URL: {bool(url)}, KEY: {bool(key)}")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise ValueError(f"Failed to create Supabase client. Error: {e}")


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
def get_all_events(filter_type='all', industry=None):
    """Fetches events with optional filtering."""
    try:
        query = supabase.table('events').select("*")

        if industry and industry != 'all':
            query = query.eq('industry', industry)

        if filter_type == 'upcoming':
            query = query.gte('start_date', date.today().isoformat())
        elif filter_type == 'past':
            query = query.lt('start_date', date.today().isoformat())

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
    try:
        response = supabase.table('intelligence_reports') \
            .select("*") \
            .order('created_at', desc=True) \
            .execute()
        return render_template('archive.html', reports=response.data)
    except Exception as e:
        return f"<h3>Archive Crashed: {e}</h3>", 500


# --- EVENTS ROUTES ---

@app.route('/events')
def events():
    """Events listing page with filters and upcoming notifications."""
    filter_type = request.args.get('filter', 'all')
    industry = request.args.get('industry', 'all')

    events_list = get_all_events(filter_type, industry)
    today = date.today()

    # Process events for display
    upcoming_events = []
    for event in events_list:
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

    return render_template('events.html',
                           events=events_list,
                           upcoming_events=upcoming_events,
                           current_filter=filter_type,
                           current_industry=industry)


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
                    supabase.table('events').insert(event_data).execute()
                    count += 1

            return redirect(url_for('events') + f'?uploaded={count}')

        except Exception as e:
            return render_template('upload_events.html', error=f"Error processing file: {e}")

    return render_template('upload_events.html')


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

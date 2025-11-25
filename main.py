import os
import json
import ast  # <--- NEW: Add this library
from flask import Flask, render_template
from supabase import create_client, Client

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


@app.route('/preview/apple')
def preview_apple():
    return render_template('preview_apple.html')


@app.route('/preview/linear')
def preview_linear():
    return render_template('preview_linear.html')


@app.route('/preview/stripe')
def preview_stripe():
    return render_template('preview_stripe.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

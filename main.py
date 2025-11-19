import os
from flask import Flask, render_template
from supabase import create_client, Client

app = Flask(__name__)

# --- 1. SETUP SUPABASE CONNECTION ---
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError(f"Missing Supabase credentials! URL: {bool(url)}, KEY: {bool(key)}")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise ValueError(f"Failed to create Supabase client. URL length: {len(url) if url else 0}, Error: {e}")

# --- 2. ROUTES ---


@app.route('/')
def dashboard():
    """
    The Main Dashboard (The 'Face').
    Fetches the LATEST report for the Hospitality vertical.
    """
    # Query Supabase for the most recent 'hospitality' row
    response = supabase.table('intelligence_reports') \
        .select("*") \
        .eq('vertical', 'hospitality') \
        .order('created_at', desc=True) \
        .limit(1) \
        .execute()

    # If we found data, get the first item. Otherwise, None.
    latest_hospitality = response.data[0] if response.data else None

    return render_template('index.html', hospitality_data=latest_hospitality)


@app.route('/archive')
def archive():
    """
    The Archive Page (The 'Warehouse').
    Fetches ALL reports to display in a table.
    """
    response = supabase.table('intelligence_reports') \
        .select("*") \
        .order('created_at', desc=True) \
        .execute()

    all_reports = response.data

    return render_template('archive.html', reports=all_reports)


# --- 3. RUN THE APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

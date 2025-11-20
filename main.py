import os
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


@app.route('/')
def dashboard():
    """
    DEBUG MODE: Fetches ANY report (ignoring the vertical name).
    """
    print("--- DEBUG START ---")

    # 1. Query Supabase (NO FILTER)
    # We removed .eq('vertical', 'hospitality') to see if ANY data exists
    # RESTORED: The correct filter
    response = supabase.table('intelligence_reports') \
        .select("*") \
        .eq('vertical', 'hospitality') \
        .order('created_at', desc=True) \
        .limit(1) \
        .execute()

    return render_template('index.html', hospitality_data=hospitality)


@app.route('/archive')
def archive():
    response = supabase.table('intelligence_reports') \
        .select("*") \
        .order('created_at', desc=True) \
        .execute()

    all_reports = response.data

    return render_template('archive.html', reports=all_reports)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

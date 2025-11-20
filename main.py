import os
import json
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
    print("--- DASHBOARD START ---")
    try:
        # 1. Query Supabase
        response = supabase.table('intelligence_reports') \
            .select("*") \
            .eq('vertical', 'hospitality') \
            .order('created_at', desc=True) \
            .limit(1) \
            .execute()

        print(f"Database Response: {response.data}")

        # 2. Get the data (Default to empty dict {} if None)
        latest_hospitality = response.data[0] if response.data else {}

        # 3. DATA CLEANING (Type-Safe Version)
        # We check 'isinstance(..., dict)' to verify it's a real dictionary
        # before trying to edit it. This fixes the red squiggles.
        if isinstance(latest_hospitality, dict):

            # Fix Top 3 News
            top_3 = latest_hospitality.get('top_3_json')
            if isinstance(top_3, str):
                try:
                    latest_hospitality['top_3_json'] = json.loads(top_3)
                except Exception as e:
                    print(f"Error parsing Top 3 JSON: {e}")

            # Fix HTML Report
            report_html = latest_hospitality.get('report_html')
            if isinstance(report_html, str):
                latest_hospitality['report_html'] = report_html.replace(
                    '\\n', '\n').strip('"')

        # If it was empty {}, change it back to None so the template handles it correctly
        if latest_hospitality == {}:
            latest_hospitality = None

        return render_template('index.html',
                               hospitality_data=latest_hospitality)

    except Exception as e:
        print("\n!!!!!!!!!!!!!! APP CRASHED !!!!!!!!!!!!!!")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR DETAILS: {e}")
        return f"<h3>App Crashed: {e}</h3>", 500


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

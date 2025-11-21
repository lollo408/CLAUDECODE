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


# --- HELPER FUNCTION ---
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
            # Clean Top 3 JSON
            top_3 = data.get('top_3_json')
            if isinstance(top_3, str):
                try:
                    data['top_3_json'] = json.loads(top_3)
                except:
                    print(f"Error parsing JSON for {vertical_name}")

            # Clean HTML
            report_html = data.get('report_html')
            if isinstance(report_html, str):
                data['report_html'] = report_html.replace('\\n',
                                                          '\n').strip('"')

        return data
    except Exception as e:
        print(f"Error fetching {vertical_name}: {e}")
        return None


@app.route('/')
def dashboard():
    print("--- DASHBOARD START ---")

    # Fetch both verticals
    hospitality = get_latest_report('hospitality')
    automotive = get_latest_report('automotive')

    # Render with both datasets
    return render_template('index.html',
                           hospitality_data=hospitality,
                           automotive_data=automotive)


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

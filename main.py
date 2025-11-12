from flask import Flask, render_template, request, abort
from replit import db  # Imports the Replit Database
import os  # Imports the ability to read Secrets

app = Flask(__name__)

# Load your secret key from the Replit "Secrets" tab
MAKE_API_KEY = os.environ.get('MAKE_API_KEY')


# --- 1. THE PUBLIC DASHBOARD (THE "FACE") ---
# This is the URL your engineers will visit.
@app.route('/')
def dashboard():
    try:
        # Read the latest data from the Replit Database
        # Note: 'db.get()' returns 'None' if the key doesn't exist yet,
        # which is perfect for the first run.
        top_3_news = db.get("hospitality_top_3")
        full_report_html = db.get("hospitality_full_html")

        # Render the 'index.html' template and pass the data to it
        return render_template('index.html',
                               hospitality_news=top_3_news,
                               full_report=full_report_html)
    except Exception as e:
        # Return a clean error if the database fails
        return f"Error loading dashboard: {e}"


# --- 2. THE SECRET WEBHOOKS (THE "ENGINE") ---
# These are the private URLs your Make.com flow will call.


# Webhook to update the "Top 3 News"
@app.route('/update-top3', methods=['POST'])
def update_top3():
    # A. Check if the request is from Make.com (using your secret key)
    if request.headers.get('X-API-KEY') != MAKE_API_KEY:
        abort(401)  # Unauthorized

    # B. Get the new JSON data from Make.com
    new_data = request.json

    # C. Save the new data to the Replit Database
    db["hospitality_top_3"] = new_data
    return {"status": "success", "updated_key": "hospitality_top_3"}, 200


# Webhook to update the "Full Report"
@app.route('/update-full-report', methods=['POST'])
def update_full_report():
    # A. Check for the secret key
    if request.headers.get('X-API-KEY') != MAKE_API_KEY:
        abort(401)  # Unauthorized

    # B. Get the new HTML data from Make.com (sent as raw text/html)
    new_data = request.data.decode('utf-8')

    # C. Save the new data to the Replit Database
    db["hospitality_full_html"] = new_data
    return {"status": "success", "updated_key": "hospitality_full_html"}, 200


# --- 3. RUN THE APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

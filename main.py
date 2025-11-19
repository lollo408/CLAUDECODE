from flask import Flask, render_template, request, abort
from replit import db
import os

app = Flask(__name__)

MAKE_API_KEY = os.environ.get('MAKE_API_KEY')


@app.route('/')
def dashboard():
    try:
        top_3_news = db.get("hospitality_top_3")
        full_report_html = db.get("hospitality_full_html")

        return render_template('index.html',
                               hospitality_news=top_3_news,
                               full_report=full_report_html)
    except Exception as e:
        return f"Error loading dashboard: {e}"


@app.route('/update-top3', methods=['POST'])
def update_top3():
    if request.headers.get('X-API-KEY') != MAKE_API_KEY:
        abort(401)

    new_data = request.json
    db["hospitality_top_3"] = new_data
    return {"status": "success", "updated_key": "hospitality_top_3"}, 200


@app.route('/update-full-report', methods=['POST'])
def update_full_report():
    if request.headers.get('X-API-KEY') != MAKE_API_KEY:
        abort(401)

    new_data = request.data.decode('utf-8')
    db["hospitality_full_html"] = new_data
    return {"status": "success", "updated_key": "hospitality_full_html"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

"""
SSB Sustainability Dashboard - Flask Application
Piana Sustainability Calculator for Simmons Serta Bedding
"""

from flask import Flask, render_template, send_from_directory, jsonify
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Index page with links to design options"""
    return '''
    <html>
    <head>
        <title>Design Options</title>
        <style>
            body { font-family: system-ui; padding: 40px; max-width: 600px; margin: 0 auto; }
            h1 { margin-bottom: 24px; }
            a { display: block; padding: 16px 24px; margin: 12px 0; background: #f0f0f0;
                border-radius: 8px; text-decoration: none; color: #333; }
            a:hover { background: #e0e0e0; }
            .desc { font-size: 0.9rem; color: #666; margin-top: 4px; }
        </style>
    </head>
    <body>
        <h1>SSB Dashboard - Design Options</h1>
        <a href="/option-a">
            <strong>Option A - Minimal Clean</strong>
            <div class="desc">Light, airy, centered layout with lots of white space</div>
        </a>
        <a href="/option-b">
            <strong>Option B - Modern Dark</strong>
            <div class="desc">Dark theme, side panel, contemporary feel</div>
        </a>
        <a href="/option-c">
            <strong>Option C - Corporate Table</strong>
            <div class="desc">Traditional table layout, professional/enterprise style</div>
        </a>
    </body>
    </html>
    '''

@app.route('/option-a')
def option_a():
    """Option A - Minimal Clean"""
    return render_template('option-a.html')

@app.route('/option-b')
def option_b():
    """Option B - Modern Dark"""
    return render_template('option-b.html')

@app.route('/option-c')
def option_c():
    """Option C - Corporate Table"""
    return render_template('option-c.html')

@app.route('/api/products')
def get_products():
    """API endpoint to get product data"""
    json_path = os.path.join(app.static_folder, 'data', 'products.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

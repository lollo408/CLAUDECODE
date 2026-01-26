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
    """Main calculator page"""
    return render_template('calculator.html')

@app.route('/api/products')
def get_products():
    """API endpoint to get product data"""
    json_path = os.path.join(app.static_folder, 'data', 'products.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/orders-2025')
def get_orders_2025():
    """API endpoint to get 2025 SSB order data"""
    json_path = os.path.join(app.static_folder, 'data', 'orders_2025.json')
    with open(json_path, 'r') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

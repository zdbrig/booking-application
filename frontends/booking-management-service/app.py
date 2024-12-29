from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)
base_url = "http://a29cadd9-48cd-4cd8-94aa-37cbe687486a:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_bookings')
def get_bookings():
    try:
        response = requests.get(f"{base_url}/clients/")
        if response.status_code == 200:
            bookings = response.json()
            for booking in bookings:
                booking['check_in'] = datetime.fromisoformat(booking['check_in'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                booking['check_out'] = datetime.fromisoformat(booking['check_out'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
                booking['created_at'] = datetime.fromisoformat(booking['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
            return jsonify(bookings)
        return jsonify([])
    except Exception as e:
        return jsonify([])

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

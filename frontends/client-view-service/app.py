from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

BASE_URL = "http://a29cadd9-48cd-4cd8-94aa-37cbe687486a:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clients')
def get_clients():
    response = requests.get(f"{BASE_URL}/clients/")
    clients = response.json()
    
    # Group clients by email
    email_groups = defaultdict(list)
    for client in clients:
        client['id'] = str(client['id'])
        client['check_in'] = datetime.fromisoformat(client['check_in']).strftime('%Y-%m-%d %H:%M')
        client['check_out'] = datetime.fromisoformat(client['check_out']).strftime('%Y-%m-%d %H:%M')
        client['created_at'] = datetime.fromisoformat(client['created_at']).strftime('%Y-%m-%d %H:%M')
        email_groups[client['email']].append(client)
    
    # Take the most recent booking for each email
    grouped_clients = []
    for email_group in email_groups.values():
        # Sort by created_at in descending order and take the first one
        most_recent = max(email_group, key=lambda x: datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M'))
        most_recent['total_bookings'] = len(email_group)
        grouped_clients.append(most_recent)
    
    return jsonify(grouped_clients)

@app.route('/api/clients/<client_id>')
def get_client(client_id):
    response = requests.get(f"{BASE_URL}/clients/{client_id}")
    client = response.json()
    client['id'] = str(client['id'])
    client['check_in'] = datetime.fromisoformat(client['check_in']).strftime('%Y-%m-%d %H:%M')
    client['check_out'] = datetime.fromisoformat(client['check_out']).strftime('%Y-%m-%d %H:%M')
    client['created_at'] = datetime.fromisoformat(client['created_at']).strftime('%Y-%m-%d %H:%M')
    return jsonify(client)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

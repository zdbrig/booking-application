from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import requests
import json
from datetime import datetime
from functools import wraps
from oauthlib.oauth2 import WebApplicationClient
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

GOOGLE_CLIENT_ID = "id"
GOOGLE_CLIENT_SECRET = "zi9let"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

client = WebApplicationClient(GOOGLE_CLIENT_ID)

base_url = "http://24149b93-5fe2-4c26-94b9-508f74f73313:5000"
room_service_url = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@app.route('/login/callback')
def callback():
    code = request.args.get("code")
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    client.parse_request_body_response(json.dumps(token_response.json()))
    
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    
    if userinfo_response.json().get("email_verified"):
        session['user'] = userinfo_response.json()
        return redirect(url_for('room_page', room_id=1))
    return "User email not verified", 400

@app.route('/room/<room_id>')
@login_required
def room_page(room_id):
    try:
        booking_response = requests.get(f"{base_url}/booking/rooms/{room_id}")
        booking_data = booking_response.json()
        
        room_response = requests.get(f"{room_service_url}/rooms/{room_id}")
        room_details = room_response.json()
        
        room_data = {
            **booking_data,
            **room_details
        }
        
        return render_template('booking.html', room=room_data, user=session['user'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/book', methods=['POST'])
@login_required
def book_room():
    try:
        data = request.json
        response = requests.post(f"{base_url}/booking/book", json={
            "check_in": data['check_in'],
            "check_out": data['check_out'],
            "email": data['email'],
            "name": data['name'],
            "phone": data['phone'],
            "room_number": data['room_number']
        })
        return response.json()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

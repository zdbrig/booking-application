from flask import Flask, render_template, jsonify
import requests
import json
from datetime import datetime
import threading

app = Flask(__name__)

ROOM_SERVICE = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
CLIENT_SERVICE = "http://a29cadd9-48cd-4cd8-94aa-37cbe687486a:5000"
BOOKING_SERVICE = "http://24149b93-5fe2-4c26-94b9-508f74f73313:5000"
RATING_SERVICE = "http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dashboard/data')
def get_dashboard_data():
    try:
        rooms = requests.get(f"{ROOM_SERVICE}/rooms/").json()
        clients = requests.get(f"{CLIENT_SERVICE}/clients/").json()
        availability = requests.get(f"{BOOKING_SERVICE}/booking/rooms").json()
        
        for room in rooms:
            try:
                rating_response = requests.get(f"{RATING_SERVICE}/ratings/room/{room['id']}/average")
                room['average_rating'] = rating_response.json() if rating_response.status_code == 200 else None
            except:
                room['average_rating'] = None
        
        return jsonify({
            'rooms': rooms,
            'clients': clients,
            'availability': availability
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

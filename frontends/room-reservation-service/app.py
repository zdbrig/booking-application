from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)
base_url = "http://24149b93-5fe2-4c26-94b9-508f74f73313:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/<room_id>')
def room_booking(room_id):
    response = requests.get(f"{base_url}/booking/rooms/{room_id}")
    room_data = response.json()
    return render_template('room_booking.html', room=room_data)

@app.route('/api/book', methods=['POST'])
def book_room():
    data = request.json
    booking_data = {
        "check_in": datetime.fromisoformat(data['checkIn'].replace('Z', '+00:00')).isoformat(),
        "check_out": datetime.fromisoformat(data['checkOut'].replace('Z', '+00:00')).isoformat(),
        "email": data['email'],
        "name": data['name'],
        "phone": data['phone'],
        "room_number": int(data['roomNumber'])
    }
    response = requests.post(f"{base_url}/booking/book", json=booking_data)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

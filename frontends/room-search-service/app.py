from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

ROOMS_SERVICE = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
BOOKING_SERVICE = "http://24149b93-5fe2-4c26-94b9-508f74f73313:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms')
def get_rooms():
    rooms_response = requests.get(f"{ROOMS_SERVICE}/rooms/")
    availability_response = requests.get(f"{BOOKING_SERVICE}/booking/rooms")
    
    if rooms_response.status_code == 200 and availability_response.status_code == 200:
        rooms = rooms_response.json()
        availability = availability_response.json()
        
        for room in rooms:
            room_availability = next((a for a in availability if a['number'] == room['id']), None)
            if room_availability:
                room['availability'] = room_availability['available']
        
        return jsonify(rooms)
    return jsonify([])

@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    data = request.json
    check_in = data.get('check_in')
    check_out = data.get('check_out')
    room_id = data.get('room_id')
    
    room_response = requests.get(f"{BOOKING_SERVICE}/booking/rooms/{room_id}")
    if room_response.status_code == 200:
        room_data = room_response.json()
        return jsonify(room_data)
    return jsonify({"error": "Room not found"}), 404

@app.route('/api/book', methods=['POST'])
def book_room():
    booking_data = request.json
    booking_response = requests.post(f"{BOOKING_SERVICE}/booking/book", json=booking_data)
    
    if booking_response.status_code == 200:
        return jsonify(booking_response.json())
    return jsonify({"error": "Booking failed"}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)


from flask import Flask
from flask_restx import Api, Resource, fields
import requests
import json
from datetime import datetime

app = Flask(__name__)
api = Api(app)
ns = api.namespace('booking', description='Booking operations')

room_service_host = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
client_service_host = "http://a29cadd9-48cd-4cd8-94aa-37cbe687486a:5000"

room_model = api.model('Room', {
    'id': fields.String(required=True),
    'number': fields.Integer(required=True),
    'available': fields.Boolean(required=True)
})

booking_input = api.model('BookingInput', {
    'check_in': fields.String(required=True, description='Check-in date (ISO 8601)'),
    'check_out': fields.String(required=True, description='Check-out date (ISO 8601)'),
    'email': fields.String(required=True),
    'name': fields.String(required=True),
    'phone': fields.String(required=True),
    'room_number': fields.Integer(required=True)
})

booking_response = api.model('BookingResponse', {
    'status': fields.String(required=True),
    'booking_id': fields.String(required=True)
})

booking_details = api.model('BookingDetails', {
    'id': fields.String(required=True),
    'check_in': fields.String(required=True),
    'check_out': fields.String(required=True),
    'email': fields.String(required=True),
    'name': fields.String(required=True),
    'phone': fields.String(required=True),
    'room_number': fields.Integer(required=True)
})

@ns.route('/rooms')
class RoomList(Resource):
    @ns.marshal_list_with(room_model)
    def get(self):
        response = requests.get(f"{room_service_host}/rooms/")
        return response.json()

@ns.route('/rooms/<string:room_id>')
class Room(Resource):
    @ns.marshal_with(room_model)
    def get(self, room_id):
        response = requests.get(f"{room_service_host}/rooms/{room_id}")
        return response.json()

@ns.route('/book')
class Booking(Resource):
    @ns.expect(booking_input)
    @ns.marshal_with(booking_response)
    def post(self):
        data = api.payload
        
        # Validate dates
        try:
            check_in = datetime.fromisoformat(data['check_in'])
            check_out = datetime.fromisoformat(data['check_out'])
            if check_in >= check_out:
                api.abort(400, "Check-out must be after check-in")
        except ValueError:
            api.abort(400, "Invalid date format. Use ISO 8601")

        # Check room availability
        room_status = requests.get(f"{client_service_host}/clients/room/{data['room_number']}")
        if room_status.status_code == 200:
            api.abort(400, "Room is not available for the selected dates")

        # Create booking
        booking_response = requests.post(f"{client_service_host}/clients/", json=data)
        if booking_response.status_code != 200:
            api.abort(500, "Failed to create booking")

        booking_data = booking_response.json()
        return {
            'status': 'success',
            'booking_id': str(booking_data.get('id', ''))
        }

@ns.route('/clients/<string:booking_id>')
class BookingDetails(Resource):
    @ns.marshal_with(booking_details)
    def get(self, booking_id):
        response = requests.get(f"{client_service_host}/clients/{booking_id}")
        if response.status_code != 200:
            api.abort(404, "Booking not found")
        return response.json()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

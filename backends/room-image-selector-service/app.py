from flask import Flask
from flask_restx import Api, Resource, fields
import requests
from minio import Minio
import random
import json

app = Flask(__name__)
api = Api(app)
ns = api.namespace('rooms', description='Room operations')

room_model = api.model('Room', {
    'id': fields.String(required=True),
    'images': fields.List(fields.String),
    'description': fields.String,
    'number': fields.String,
    'price': fields.Float,
    'type': fields.String
})

minio_client = Minio(
    "minio.block-gpt.io",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)

def get_random_images_from_minio(count=3):
    objects = list(minio_client.list_objects('sqoin'))
    if not objects:
        return []
    selected_objects = random.sample(objects, min(count, len(objects)))
    return [f"https://minio.block-gpt.io/sqoin/{obj.object_name}" for obj in selected_objects]

@ns.route('/update_room_images')
class UpdateRoomImages(Resource):
    @ns.marshal_with(room_model)
    def post(self):
        try:
            # Get all rooms
            response = requests.get('http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/')
            rooms = response.json()

            for room in rooms:
                # Get new random images
                new_images = get_random_images_from_minio()
                
                # Update room with new images
                room['images'] = new_images
                
                # Update the room via API
                update_response = requests.put(
                    f'http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/{room["id"]}',
                    json=room
                )
                
                if update_response.status_code != 200:
                    raise Exception(f"Failed to update room {room['id']}")

            return rooms

        except Exception as e:
            api.abort(500, str(e))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

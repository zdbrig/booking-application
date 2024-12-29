from flask import Flask, render_template, request, jsonify
import requests
import os
from minio import Minio
import json

app = Flask(__name__)

MINIO_CLIENT = Minio(
    "minio.block-gpt.io",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)

ROOM_IMAGES = [
    "room1.jpg",
    "room2.jpg", 
    "room3.jpg",
    "room4.jpg",
    "room5.jpg"
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_room_images/<room_id>', methods=['POST'])
def update_room_images(room_id):
    try:
        # First get current room details
        response = requests.get(f'http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/{room_id}')
        room_data = response.json()
        
        # Generate presigned URLs for room images
        image_urls = []
        for image in ROOM_IMAGES:
            try:
                url = MINIO_CLIENT.presigned_get_object('sqoin', image)
                image_urls.append(url)
            except:
                continue
                
        # Update room data with new images
        room_data['images'] = image_urls
        
        # Update room via API
        update_response = requests.put(
            f'http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/{room_id}',
            json=room_data
        )
        
        return jsonify({"success": True, "message": "Room images updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

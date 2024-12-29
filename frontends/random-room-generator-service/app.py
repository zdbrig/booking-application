from flask import Flask, jsonify, render_template
import requests
import random
from minio import Minio
import json

app = Flask(__name__)

def get_minio_images():
    client = Minio(
        "minio.block-gpt.io",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=True
    )
    images = []
    objects = client.list_objects("sqoin")
    for obj in objects:
        images.append(f"https://minio.block-gpt.io/sqoin/{obj.object_name}")
    return images

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert_rooms')
def insert_rooms():
    images = get_minio_images()
    room_types = ["Single", "Double", "Suite", "Deluxe", "Presidential"]
    options = [
        {"name": "WiFi", "description": "High-speed internet"},
        {"name": "Breakfast", "description": "Continental breakfast"},
        {"name": "Mini Bar", "description": "Fully stocked mini bar"},
        {"name": "Room Service", "description": "24/7 room service"},
        {"name": "Spa Access", "description": "Access to hotel spa"}
    ]
    
    for _ in range(30):
        room_data = {
            "description": f"Beautiful {random.choice(room_types)} room with amazing view",
            "number": str(random.randint(100, 999)),
            "price": random.randint(100, 1000),
            "type": random.choice(room_types),
            "images": random.sample(images, min(3, len(images))),
            "options": random.sample(options, random.randint(2, 5))
        }
        
        requests.post(f"{host}/rooms/", json=room_data)
    
    return jsonify({"message": "30 rooms inserted successfully"})

host = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

import os
from flask import Flask
from flask_restx import Api, Resource
import requests
from serpapi import GoogleSearch
from minio import Minio
import logging
from logging.handlers import RotatingFileHandler
import json
import urllib.request
import uuid

# Setup logging
logger = logging.getLogger('room_image_updater')
logger.setLevel(logging.DEBUG)

fh = RotatingFileHandler('room_updater.log', maxBytes=1000000, backupCount=3)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

app = Flask(__name__)
api = Api(app)

# Minio configuration
minio_client = Minio(
    "minio.block-gpt.io",
    secure=True,
    access_key="minioadmin",
    secret_key="minioadmin"
)

ROOMS_API = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
SERP_API_KEY = "b6c4a1f1b3f2a737a8d3fef1c2e307f0deff2b2f"

def search_hotel_room_images(query, num_images=3):
    params = {
        "engine": "google_images",
        "q": f"hotel room {query}",
        "num": num_images,
        "api_key": SERP_API_KEY
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    return [img["original"] for img in results.get("images_results", [])]

def upload_to_minio(image_url):
    try:
        temp_file = f"/tmp/{uuid.uuid4()}.jpg"
        urllib.request.urlretrieve(image_url, temp_file)
        
        file_name = f"room_images/{uuid.uuid4()}.jpg"
        minio_client.fput_object("sqoin", file_name, temp_file)
        os.remove(temp_file)
        
        return f"https://minio.block-gpt.io/sqoin/{file_name}"
    except Exception as e:
        logger.error(f"Error uploading to Minio: {str(e)}")
        return None

@api.route('/update-room-images')
class RoomImageUpdater(Resource):
    def post(self):
        try:
            # Clear existing bucket
            objects = minio_client.list_objects("sqoin", prefix="room_images/")
            for obj in objects:
                minio_client.remove_object("sqoin", obj.object_name)
            logger.info("Cleared existing images from Minio bucket")

            # Get all rooms
            response = requests.get(f"{ROOMS_API}/rooms/")
            rooms = response.json()
            
            for room in rooms:
                room_id = room['id']
                room_type = room.get('room_type', 'luxury hotel room')
                
                # Search for new images
                new_images = search_hotel_room_images(room_type)
                
                # Upload to Minio and get URLs
                minio_urls = []
                for img_url in new_images:
                    minio_url = upload_to_minio(img_url)
                    if minio_url:
                        minio_urls.append(minio_url)
                
                # Update room with new images
                room['images'] = minio_urls
                update_response = requests.put(
                    f"{ROOMS_API}/rooms/{room_id}",
                    json=room
                )
                
                logger.info(f"Updated room {room_id} with new images")
                
            return {"message": "Successfully updated all room images"}
            
        except Exception as e:
            logger.error(f"Error updating room images: {str(e)}")
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

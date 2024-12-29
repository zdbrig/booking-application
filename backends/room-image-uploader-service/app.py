import os
import logging
from logging.handlers import RotatingFileHandler
import requests
from serpapi import GoogleSearch
from minio import Minio
from minio.error import S3Error
import json
from flask import Flask
from flask_restx import Api, Resource, Namespace

# Create necessary directories
os.makedirs('/app/data', exist_ok=True)

# Configure logging
logger = logging.getLogger('room_image_updater')
logger.setLevel(logging.DEBUG)

fh = RotatingFileHandler('/app/data/room_updater.log', maxBytes=1000000, backupCount=3)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# Initialize Minio client
minio_client = Minio(
    "minio.block-gpt.io",
    secure=True,
    access_key="minioadmin",
    secret_key="minioadmin"
)

app = Flask(__name__)
api = Api(app)
ns = Namespace('rooms')
api.add_namespace(ns)

@ns.route('/update-images')
class RoomImageUpdater(Resource):
    def post(self):
        try:
            # Clear Minio bucket
            try:
                objects = minio_client.list_objects('sqoin')
                for obj in objects:
                    minio_client.remove_object('sqoin', obj.object_name)
                logger.info("Cleared Minio bucket 'sqoin'")
            except S3Error as e:
                logger.error(f"Error clearing Minio bucket: {str(e)}")

            # Get all rooms
            rooms_response = requests.get("http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/")
            rooms = rooms_response.json()

            for room in rooms:
                # Search for hotel room images
                params = {
                    "api_key": "b6c4a1f1b3f2a737a8d3fef1c2e307f0deff2b2f",
                    "engine": "google_images",
                    "q": f"luxury hotel room {room['type']}",
                    "num": 3
                }
                search = GoogleSearch(params)
                results = search.get_dict()

                new_images = []
                for idx, image in enumerate(results.get('images_results', [])[:3]):
                    image_url = image['original']
                    
                    # Download image
                    img_response = requests.get(image_url)
                    if img_response.status_code == 200:
                        # Upload to Minio
                        object_name = f"room_{room['_id']}_{idx}.jpg"
                        minio_client.put_object(
                            'sqoin',
                            object_name,
                            img_response.content,
                            len(img_response.content),
                            'image/jpeg'
                        )
                        new_images.append(f"https://minio.block-gpt.io/sqoin/{object_name}")

                # Update room with new images
                if new_images:
                    update_response = requests.put(
                        f"http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/{room['_id']}",
                        json={**room, 'images': new_images}
                    )
                    logger.info(f"Updated room {room['_id']} with new images")

            return {"message": "Room images updated successfully"}, 200

        except Exception as e:
            logger.error(f"Error updating room images: {str(e)}")
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

from flask import Flask, request, jsonify
from serpapi import GoogleSearch
from minio import Minio
import requests
import os
import uuid
import logging
import sys

# Configure logging to output to both console and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Minio configuration
minio_client = Minio(
    "minio.block-gpt.io",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)

# Ensure the bucket exists
bucket_name = "sqoin"
try:
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        logger.info(f"Created new bucket: {bucket_name}")
    else:
        logger.info(f"Bucket {bucket_name} exists, clearing existing objects")
        # Clear existing objects in the bucket
        objects = minio_client.list_objects(bucket_name)
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
            logger.info(f"Removed object: {obj.object_name}")

except Exception as e:
    logger.error(f"Error with Minio bucket operations: {str(e)}")
    raise

@app.route('/rooms/update_room_images', methods=['POST'])
def update_room_images():
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400

        search_query = data.get('search_query', '')
        room_id = data.get('room_id')

        if not search_query:
            logger.error("No search query provided")
            return jsonify({'error': 'Search query is required'}), 400

        logger.info(f"Processing image search for query: {search_query}")

        # Search for images using SerpAPI
        params = {
            "q": search_query,
            "tbm": "isch",
            "api_key": "b6c4a1f1b3f2a737a8d3fef1c2e307f0deff2b2f"
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        image_results = results.get('images_results', [])

        if not image_results:
            logger.warning("No images found for the search query")
            return jsonify({'message': 'No images found'}), 404

        # Download and upload images to Minio
        uploaded_urls = []
        for idx, image in enumerate(image_results[:5]):  # Limit to first 5 images
            image_url = image.get('original')
            if not image_url:
                logger.warning(f"No URL found for image {idx+1}")
                continue

            try:
                logger.info(f"Downloading image from: {image_url}")
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()

                # Generate unique filename
                filename = f"{uuid.uuid4()}.jpg"
                
                # Upload to Minio
                minio_client.put_object(
                    bucket_name,
                    filename,
                    response.content,
                    length=len(response.content),
                    content_type='image/jpeg'
                )
                
                uploaded_url = f"https://minio.block-gpt.io/{bucket_name}/{filename}"
                uploaded_urls.append(uploaded_url)
                logger.info(f"Successfully uploaded image to: {uploaded_url}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Error downloading image: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                continue

        if not uploaded_urls:
            logger.error("No images were successfully uploaded")
            return jsonify({'error': 'Failed to upload any images'}), 500

        # Update room with new image URLs
        if room_id:
            try:
                room_service_url = f"http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000/rooms/{room_id}"
                logger.info(f"Updating room {room_id} with new images")
                
                room_response = requests.get(room_service_url)
                room_response.raise_for_status()
                
                room_data = room_response.json()
                room_data['images'] = uploaded_urls
                
                update_response = requests.put(room_service_url, json=room_data)
                update_response.raise_for_status()
                
                logger.info(f"Successfully updated room {room_id} with new images")
                return jsonify({'message': 'Room images updated successfully', 'urls': uploaded_urls})

            except requests.exceptions.RequestException as e:
                logger.error(f"Error updating room: {str(e)}")
                return jsonify({'error': f"Failed to update room: {str(e)}"}), 500

        return jsonify({'message': 'Images uploaded successfully', 'urls': uploaded_urls})

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

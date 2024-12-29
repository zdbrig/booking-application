from flask import Flask
from flask_restx import Api, Resource, Namespace
import requests
import random
import time
import threading

app = Flask(__name__)
api = Api(app)
ns = Namespace('generator')
api.add_namespace(ns)

ROOM_SERVICE_HOST = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
RATING_SERVICE_HOST = "http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000"
COMMENTS = [
    "Great room, loved the view!",
    "Clean and comfortable",
    "Excellent service",
    "Could be better",
    "Amazing experience",
    "Decent stay",
    "Perfect location",
    "Very spacious",
    "Good value for money",
    "Would recommend"
]

def generate_random_rating():
    return random.randint(1, 5)

def generate_random_guest_id():
    return f"guest_{random.randint(1000, 9999)}"

def generate_ratings():
    while True:
        try:
            # Get all rooms
            rooms_response = requests.get(f"{ROOM_SERVICE_HOST}/rooms/")
            rooms = rooms_response.json()

            for room in rooms:
                # Generate 3-5 ratings per room
                num_ratings = random.randint(3, 5)
                for _ in range(num_ratings):
                    rating_data = {
                        "guest_id": generate_random_guest_id(),
                        "room_id": room["id"],
                        "rating": generate_random_rating(),
                        "comment": random.choice(COMMENTS)
                    }
                    
                    # Post rating to rating service
                    requests.post(f"{RATING_SERVICE_HOST}/ratings", json=rating_data)
                
                time.sleep(1)  # Avoid overwhelming the service
            
            time.sleep(60)  # Wait before next batch
            
        except Exception as e:
            print(f"Error generating ratings: {str(e)}")
            time.sleep(10)

@ns.route('/start')
class RatingGenerator(Resource):
    def post(self):
        thread = threading.Thread(target=generate_ratings, daemon=True)
        thread.start()
        return {"message": "Rating generation started"}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)


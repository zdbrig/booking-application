from flask import Flask, jsonify
import requests
import random
import json
from flask_restx import Api, Resource, Namespace

app = Flask(__name__)
api = Api(app)
ns = Namespace('ratings')
api.add_namespace(ns)

def get_all_rooms():
    try:
        response = requests.get('http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000/rooms')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def generate_random_comment():
    comments = [
        "Great room, highly recommended!",
        "Nice view and comfortable bed",
        "Clean and spacious",
        "Excellent service",
        "Good value for money",
        "Perfect location",
        "Could be better",
        "Decent stay",
        "Amazing experience",
        "Very comfortable"
    ]
    return random.choice(comments)

@ns.route('/generate-ratings')
class GenerateRatings(Resource):
    def post(self):
        rooms = get_all_rooms()
        generated_ratings = []
        
        for room in rooms:
            num_ratings = random.randint(5, 15)
            for _ in range(num_ratings):
                rating_data = {
                    "guest_id": f"guest_{random.randint(1000, 9999)}",
                    "room_id": room['_id'],
                    "rating": random.randint(1, 5),
                    "comment": generate_random_comment()
                }
                
                response = requests.post(
                    'http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000/ratings',
                    json=rating_data
                )
                if response.status_code == 200:
                    generated_ratings.append(response.json())
                
        return {"message": "Ratings generated successfully", "ratings": generated_ratings}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

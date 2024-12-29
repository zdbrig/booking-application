from flask import Flask
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

app = Flask(__name__)
api = Api(app)
ns = api.namespace('ratings', description='Rating operations')

client = MongoClient('mongodb://mongodb:27017/')
db = client.hotel_db

rating_model = api.model('Rating', {
    'id': fields.String(readonly=True, description='Rating ID'),
    'room_id': fields.String(required=True, description='Room ID'),
    'guest_id': fields.String(required=True, description='Guest ID'),
    'rating': fields.Integer(required=True, min=1, max=5, description='Rating value'),
    'comment': fields.String(required=False, description='Review comment'),
    'created_at': fields.DateTime(readonly=True, description='Rating timestamp')
})

rating_input = api.model('RatingInput', {
    'room_id': fields.String(required=True, description='Room ID'),
    'guest_id': fields.String(required=True, description='Guest ID'),
    'rating': fields.Integer(required=True, min=1, max=5, description='Rating value'),
    'comment': fields.String(required=False, description='Review comment')
})

@ns.route('')
class RatingList(Resource):
    @ns.expect(rating_input)
    @ns.marshal_with(rating_model)
    def post(self):
        data = api.payload
        rating_doc = {
            'room_id': data['room_id'],
            'guest_id': data['guest_id'],
            'rating': data['rating'],
            'comment': data.get('comment', ''),
            'created_at': datetime.utcnow().isoformat()
        }
        result = db.ratings.insert_one(rating_doc)
        rating_doc['id'] = str(result.inserted_id)
        return rating_doc

@ns.route('/room/<string:room_id>')
class RoomRatings(Resource):
    @ns.marshal_list_with(rating_model)
    def get(self, room_id):
        ratings = list(db.ratings.find({'room_id': room_id}))
        for rating in ratings:
            rating['id'] = str(rating['_id'])
            del rating['_id']
        return ratings

@ns.route('/guest/<string:guest_id>')
class GuestRatings(Resource):
    @ns.marshal_list_with(rating_model)
    def get(self, guest_id):
        ratings = list(db.ratings.find({'guest_id': guest_id}))
        for rating in ratings:
            rating['id'] = str(rating['_id'])
            del rating['_id']
        return ratings

@ns.route('/room/<string:room_id>/average')
class RoomAverageRating(Resource):
    def get(self, room_id):
        pipeline = [
            {'$match': {'room_id': room_id}},
            {'$group': {'_id': None, 'average': {'$avg': '$rating'}}}
        ]
        result = list(db.ratings.aggregate(pipeline))
        if result:
            return {'room_id': room_id, 'average_rating': round(result[0]['average'], 2)}
        return {'room_id': room_id, 'average_rating': 0}

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

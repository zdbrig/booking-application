from flask import Flask
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
import json
from bson import ObjectId
from minio import Minio

app = Flask(__name__)
api = Api(app)
ns = api.namespace('rooms', description='Room management operations')

client = MongoClient('mongodb://mongodb:27017/')
db = client['guesthouse']
rooms_collection = db['rooms']

minio_client = Minio(
    "minio.block-gpt.io",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=True
)

room_option = api.model('RoomOption', {
    'name': fields.String(required=True, description='Option name'),
    'description': fields.String(required=True, description='Option description')
})

room = api.model('Room', {
    'id': fields.String(description='Room ID'),
    'number': fields.String(required=True, description='Room number'),
    'type': fields.String(required=True, description='Room type'),
    'price': fields.Float(required=True, description='Room price per night'),
    'description': fields.String(required=True, description='Room description'),
    'options': fields.List(fields.Nested(room_option), description='Room options'),
    'images': fields.List(fields.String, description='Room image URLs')
})

@ns.route('/')
class RoomList(Resource):
    @ns.marshal_list_with(room)
    def get(self):
        rooms = list(rooms_collection.find())
        for room in rooms:
            room['id'] = str(room['_id'])
            del room['_id']
        return rooms

    @ns.expect(room)
    @ns.marshal_with(room)
    def post(self):
        data = api.payload
        result = rooms_collection.insert_one(data)
        data['id'] = str(result.inserted_id)
        return data

@ns.route('/<string:id>')
class Room(Resource):
    @ns.marshal_with(room)
    def get(self, id):
        room = rooms_collection.find_one({'_id': ObjectId(id)})
        if room:
            room['id'] = str(room['_id'])
            del room['_id']
            return room
        api.abort(404, f"Room {id} not found")

    @ns.expect(room)
    @ns.marshal_with(room)
    def put(self, id):
        data = api.payload
        result = rooms_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )
        if result.modified_count:
            room = rooms_collection.find_one({'_id': ObjectId(id)})
            room['id'] = str(room['_id'])
            del room['_id']
            return room
        api.abort(404, f"Room {id} not found")

    def delete(self, id):
        result = rooms_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return {'message': f'Room {id} deleted'}
        api.abort(404, f"Room {id} not found")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

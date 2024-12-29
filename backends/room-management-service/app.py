from flask import Flask, jsonify
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from bson import ObjectId
import json

app = Flask(__name__)
api = Api(app)
ns = api.namespace('rooms', description='Rooms operations')

client = MongoClient('mongodb://mongodb:27017/')
db = client['hotel']
rooms_collection = db['rooms']

room_option = api.model('RoomOption', {
    'name': fields.String(required=True),
    'value': fields.String(required=True)
})

room_model = api.model('Room', {
    'id': fields.String(attribute='_id'),
    'description': fields.String(required=True),
    'number': fields.String(required=True),
    'price': fields.Float(required=True),
    'type': fields.String(required=True),
    'images': fields.List(fields.String),
    'options': fields.List(fields.Nested(room_option))
})

room_input = api.model('RoomInput', {
    'description': fields.String(required=True),
    'number': fields.String(required=True),
    'price': fields.Float(required=True),
    'type': fields.String(required=True),
    'images': fields.List(fields.String),
    'options': fields.List(fields.Nested(room_option))
})

@ns.route('/')
class RoomList(Resource):
    @ns.marshal_list_with(room_model)
    def get(self):
        rooms = list(rooms_collection.find())
        for room in rooms:
            room['_id'] = str(room['_id'])
        return rooms

    @ns.expect(room_input)
    def post(self):
        data = api.payload
        result = rooms_collection.insert_one(data)
        data['_id'] = str(result.inserted_id)
        return jsonify(data)

@ns.route('/<string:id>')
class Room(Resource):
    @ns.marshal_with(room_model)
    def get(self, id):
        room = rooms_collection.find_one({'_id': ObjectId(id)})
        if room:
            room['_id'] = str(room['_id'])
            return room
        api.abort(404, f"Room {id} not found")

    @ns.expect(room_input)
    @ns.marshal_with(room_model)
    def put(self, id):
        data = api.payload
        result = rooms_collection.update_one({'_id': ObjectId(id)}, {'$set': data})
        if result.modified_count:
            room = rooms_collection.find_one({'_id': ObjectId(id)})
            room['_id'] = str(room['_id'])
            return room
        api.abort(404, f"Room {id} not found")

    def delete(self, id):
        result = rooms_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return {'message': f'Room {id} deleted successfully'}
        api.abort(404, f"Room {id} not found")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

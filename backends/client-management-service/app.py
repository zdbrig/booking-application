from flask import Flask
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

app = Flask(__name__)
api = Api(app)
ns = api.namespace('clients', description='Client Management Operations')

client = MongoClient('mongodb://mongodb:27017/')
db = client['guesthouse']
clients_collection = db['clients']

client_model = api.model('Client', {
    'id': fields.String(readonly=True, description='Client unique identifier'),
    'name': fields.String(required=True, description='Client name'),
    'email': fields.String(required=True, description='Client email'),
    'phone': fields.String(required=True, description='Client phone number'),
    'room_number': fields.Integer(required=True, description='Booked room number'),
    'check_in': fields.DateTime(required=True, description='Check-in date'),
    'check_out': fields.DateTime(required=True, description='Check-out date'),
    'created_at': fields.DateTime(readonly=True, description='Record creation date')
})

client_input = api.model('ClientInput', {
    'name': fields.String(required=True, description='Client name'),
    'email': fields.String(required=True, description='Client email'),
    'phone': fields.String(required=True, description='Client phone number'),
    'room_number': fields.Integer(required=True, description='Booked room number'),
    'check_in': fields.String(required=True, description='Check-in date (ISO 8601)'),
    'check_out': fields.String(required=True, description='Check-out date (ISO 8601)')
})

@ns.route('/')
class ClientList(Resource):
    @ns.marshal_list_with(client_model)
    def get(self):
        clients = clients_collection.find()
        return [{**client, 'id': str(client['_id'])} for client in clients]

    @ns.expect(client_input)
    @ns.marshal_with(client_model)
    def post(self):
        data = api.payload
        data['check_in'] = datetime.fromisoformat(data['check_in'])
        data['check_out'] = datetime.fromisoformat(data['check_out'])
        data['created_at'] = datetime.utcnow()
        
        result = clients_collection.insert_one(data)
        client = clients_collection.find_one({'_id': result.inserted_id})
        return {**client, 'id': str(client['_id'])}

@ns.route('/<string:id>')
class Client(Resource):
    @ns.marshal_with(client_model)
    def get(self, id):
        client = clients_collection.find_one({'_id': ObjectId(id)})
        if client:
            return {**client, 'id': str(client['_id'])}
        api.abort(404, f"Client {id} not found")

    @ns.expect(client_input)
    @ns.marshal_with(client_model)
    def put(self, id):
        data = api.payload
        data['check_in'] = datetime.fromisoformat(data['check_in'])
        data['check_out'] = datetime.fromisoformat(data['check_out'])
        
        result = clients_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': data}
        )
        
        if result.modified_count:
            client = clients_collection.find_one({'_id': ObjectId(id)})
            return {**client, 'id': str(client['_id'])}
        api.abort(404, f"Client {id} not found")

    def delete(self, id):
        result = clients_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count:
            return {'message': f'Client {id} deleted'}
        api.abort(404, f"Client {id} not found")

@ns.route('/room/<int:room_number>')
class ClientByRoom(Resource):
    @ns.marshal_with(client_model)
    def get(self, room_number):
        client = clients_collection.find_one({'room_number': room_number})
        if client:
            return {**client, 'id': str(client['_id'])}
        api.abort(404, f"No client found in room {room_number}")

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

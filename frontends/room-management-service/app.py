from flask import Flask, render_template, jsonify, request
import requests
import json

app = Flask(__name__)
base_url = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms', methods=['GET'])
def get_rooms():
    response = requests.get(f"{base_url}/rooms/")
    return jsonify(response.json())

@app.route('/rooms/<id>', methods=['GET'])
def get_room(id):
    response = requests.get(f"{base_url}/rooms/{id}")
    return jsonify(response.json())

@app.route('/rooms', methods=['POST'])
def create_room():
    data = request.json
    response = requests.post(f"{base_url}/rooms/", json=data)
    return jsonify(response.json())

@app.route('/rooms/<id>', methods=['PUT'])
def update_room(id):
    data = request.json
    response = requests.put(f"{base_url}/rooms/{id}", json=data)
    return jsonify(response.json())

@app.route('/rooms/<id>', methods=['DELETE'])
def delete_room(id):
    response = requests.delete(f"{base_url}/rooms/{id}")
    return jsonify({"message": "Room deleted successfully"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

from flask import Flask, render_template, request, jsonify
import requests
import json
from math import ceil

app = Flask(__name__)

BASE_URL = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
RATING_URL = "http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000"
ITEMS_PER_PAGE = 6

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    response = requests.get(f"{BASE_URL}/rooms/")
    rooms = response.json()
    
    if search:
        rooms = [room for room in rooms if search.lower() in room['description'].lower() 
                or search.lower() in room['type'].lower() 
                or search.lower() in room['number'].lower()]
    
    # Get ratings for each room
    for room in rooms:
        try:
            rating_response = requests.get(f"{RATING_URL}/ratings/room/{room['id']}/average")
            if rating_response.status_code == 200:
                room['average_rating'] = round(float(rating_response.text), 1)
            else:
                room['average_rating'] = None
        except:
            room['average_rating'] = None
    
    total_items = len(rooms)
    total_pages = ceil(total_items / ITEMS_PER_PAGE)
    
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    paginated_rooms = rooms[start_idx:end_idx]
    
    return render_template('index.html', 
                         rooms=paginated_rooms,
                         page=page,
                         total_pages=total_pages,
                         search=search)

@app.route('/room/<room_id>')
def room_detail(room_id):
    response = requests.get(f"{BASE_URL}/rooms/{room_id}")
    room = response.json()
    return render_template('room_detail.html', room=room)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)


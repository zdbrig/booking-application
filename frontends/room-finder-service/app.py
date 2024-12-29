from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import json

app = Flask(__name__)
base_url = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    price_min = request.args.get('price_min')
    price_max = request.args.get('price_max')
    room_type = request.args.get('type')
    
    response = requests.get(f"{base_url}/rooms/")
    rooms = response.json()
    
    filtered_rooms = rooms
    if price_min:
        filtered_rooms = [r for r in filtered_rooms if r['price'] >= float(price_min)]
    if price_max:
        filtered_rooms = [r for r in filtered_rooms if r['price'] <= float(price_max)]
    if room_type:
        filtered_rooms = [r for r in filtered_rooms if r['type'].lower() == room_type.lower()]
    
    return redirect(url_for('results', rooms=json.dumps(filtered_rooms)))

@app.route('/results')
def results():
    rooms = json.loads(request.args.get('rooms', '[]'))
    return render_template('results.html', rooms=rooms)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

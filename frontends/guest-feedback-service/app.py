from flask import Flask, render_template, jsonify
import requests
import json

app = Flask(__name__)

def get_ratings():
    url = "http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000/ratings/room/" 
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ratings')
def ratings():
    ratings_data = get_ratings()
    return jsonify(ratings_data)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
---END_FILE--- 


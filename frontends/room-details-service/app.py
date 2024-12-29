from flask import Flask, render_template, jsonify, request
import requests
import json
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

# Configure logging
handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Application startup')

BASE_URL = "http://600fca9d-30ef-49c7-b433-cf5480193c0d:5000"
RATING_URL = "http://4e68d551-7656-4821-a869-bef8ee3bffc1:5000"

def handle_api_error(response):
    if response.status_code == 404:
        return "Resource not found", 404
    elif response.status_code == 503:
        return "Service temporarily unavailable", 503
    elif response.status_code >= 500:
        return "Internal server error", 500
    elif response.status_code >= 400:
        return "Bad request", 400
    return "Unknown error", 500

@app.route('/room/<room_id>')
def room_detail(room_id):
    try:
        app.logger.info(f'Fetching details for room {room_id}')
        
        # Get room details
        try:
            response = requests.get(f"{BASE_URL}/rooms/{room_id}", timeout=5)
            if not response.ok:
                error_message, status_code = handle_api_error(response)
                app.logger.error(f'Room service error: {error_message}')
                return render_template('error.html', error=f"Room service error: {error_message}"), status_code
        except requests.exceptions.Timeout:
            app.logger.error('Room service timeout')
            return render_template('error.html', error="Room service is not responding. Please try again later."), 504
        except requests.exceptions.ConnectionError:
            app.logger.error('Room service connection error')
            return render_template('error.html', error="Unable to connect to room service. Please try again later."), 503
        except requests.exceptions.RequestException as e:
            app.logger.error(f'Error fetching room details: {str(e)}')
            return render_template('error.html', error="Unable to fetch room details. Please try again later."), 503

        # Get ratings
        try:
            ratings_response = requests.get(f"{RATING_URL}/ratings/room/{room_id}", timeout=5)
            if not ratings_response.ok:
                app.logger.error(f'Rating service error: {ratings_response.status_code}')
                ratings = []
            else:
                ratings = ratings_response.json()
        except requests.exceptions.RequestException as e:
            app.logger.error(f'Error fetching ratings: {str(e)}')
            ratings = []

        # Get average rating
        try:
            avg_rating_response = requests.get(f"{RATING_URL}/ratings/room/{room_id}/average", timeout=5)
            if not avg_rating_response.ok:
                app.logger.error(f'Average rating service error: {avg_rating_response.status_code}')
                avg_rating = 0
            else:
                avg_rating_data = json.loads(avg_rating_response.text)
                avg_rating = float(avg_rating_data['average_rating']) if avg_rating_data.get('average_rating') else 0
        except requests.exceptions.RequestException as e:
            app.logger.error(f'Error fetching average rating: {str(e)}')
            avg_rating = 0
        except (ValueError, json.JSONDecodeError) as e:
            app.logger.error(f'Error parsing average rating: {str(e)}')
            avg_rating = 0

        room = response.json()
        app.logger.info(f'Successfully retrieved details for room {room_id}')
        return render_template('room_detail.html', room=room, ratings=ratings, avg_rating=avg_rating)

    except Exception as e:
        app.logger.error(f'Unexpected error: {str(e)}')
        return render_template('error.html', error="An unexpected error occurred. Please try again later."), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

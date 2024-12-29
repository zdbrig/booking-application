from flask import Flask, render_template, send_file, jsonify
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Image
from reportlab.lib.units import inch
from io import BytesIO
import json
from datetime import datetime
import logging
import qrcode
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_qr_code(booking_id):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f'Booking ID: {booking_id}')
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer)
    qr_buffer.seek(0)
    return qr_buffer

def create_pdf(booking_data):
    try:
        buffer = BytesIO()
        c = canvas.Canvas(str(buffer), pagesize=A4)
        width, height = A4

        # Add hotel logo placeholder
        c.setFillColorRGB(0.2, 0.3, 0.5)
        c.rect(50, height-120, width-100, 100, fill=True)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 32)
        c.drawString(80, height-80, "LUXURY HOTEL")

        # Add decorative border
        c.setStrokeColorRGB(0.2, 0.3, 0.5)
        c.setLineWidth(2)
        c.rect(30, 30, width-60, height-60)

        # Header
        c.setFillColorRGB(0.2, 0.3, 0.5)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, height-160, "Booking Voucher")

        # Format dates
        check_in_date = datetime.fromisoformat(booking_data['check_in'].replace('Z', '+00:00'))
        check_out_date = datetime.fromisoformat(booking_data['check_out'].replace('Z', '+00:00'))
        created_date = datetime.fromisoformat(booking_data.get('created_at', datetime.now().isoformat()).replace('Z', '+00:00'))

        # Guest Information Section
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height-220, "Guest Information")
        c.setLineWidth(1)
        c.line(50, height-225, 200, height-225)

        # Details with improved formatting
        c.setFont("Helvetica", 12)
        details = [
            ("Guest Name:", booking_data['name']),
            ("Email:", booking_data['email']),
            ("Phone:", booking_data['phone']),
            ("Room Number:", str(booking_data['room_number'])),
            ("Check-in:", check_in_date.strftime('%B %d, %Y')),
            ("Check-out:", check_out_date.strftime('%B %d, %Y')),
            ("Booking ID:", booking_data['id']),
            ("Booking Date:", created_date.strftime('%B %d, %Y %H:%M'))
        ]

        y = height-250
        for label, value in details:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, label)
            c.setFont("Helvetica", 12)
            c.drawString(150, y, value)
            y -= 25

        # Add QR Code
        qr_buffer = create_qr_code(booking_data['id'])
        c.drawImage(qr_buffer, width-150, 100, width=100, height=100)

        # Add footer
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 50, "Thank you for choosing our hotel. We wish you a pleasant stay!")

        # Add terms and conditions
        c.setFont("Helvetica", 8)
        terms = [
            "Terms & Conditions:",
            "- Check-in time: 2:00 PM",
            "- Check-out time: 12:00 PM",
            "- Please present this voucher at check-in",
            "- This booking is non-refundable"
        ]
        y = 200
        for term in terms:
            c.drawString(50, y, term)
            y -= 15

        c.save()
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error creating PDF: {str(e)}")
        raise

@app.route('/booking/confirmation/<booking_id>')
def booking_confirmation(booking_id):
    try:
        logger.info(f"Fetching booking confirmation for ID: {booking_id}")
        response = requests.get(f'http://24149b93-5fe2-4c26-94b9-508f74f73313:5000/booking/clients/{booking_id}')
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch booking data. Status code: {response.status_code}")
            return jsonify({"error": f"Booking not found. Server returned {response.status_code}"}), 404
            
        booking_data = response.json()
        logger.info(f"Successfully retrieved booking data for ID: {booking_id}")
        return render_template('booking_confirmation.html', booking=booking_data)
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while fetching booking: {str(e)}")
        return jsonify({"error": "Could not connect to booking service"}), 503
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while fetching booking: {str(e)}")
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        logger.error(f"Unexpected error in booking confirmation: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/booking/voucher/<booking_id>')
def download_voucher(booking_id):
    try:
        logger.info(f"Generating voucher for booking ID: {booking_id}")
        response = requests.get(f'http://24149b93-5fe2-4c26-94b9-508f74f73313:5000/booking/clients/{booking_id}')
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch booking data for voucher. Status code: {response.status_code}")
            return jsonify({"error": f"Booking not found. Server returned {response.status_code}"}), 404
            
        booking_data = response.json()
        pdf_buffer = create_pdf(booking_data)
        logger.info(f"Successfully generated voucher for booking ID: {booking_id}")
        
        return send_file(
            pdf_buffer,
            download_name=f'booking_confirmation_{booking_id}.pdf',
            mimetype='application/pdf'
        )
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error while generating voucher: {str(e)}")
        return jsonify({"error": "Could not connect to booking service"}), 503
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout while generating voucher: {str(e)}")
        return jsonify({"error": "Request timed out"}), 504
    except Exception as e:
        logger.error(f"Unexpected error generating voucher: {str(e)}")
        return jsonify({"error": "Could not generate voucher"}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)

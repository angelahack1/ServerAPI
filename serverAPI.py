import os
import logging
from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import qrcode
from qrcode.exceptions import DataOverflowError
import sys

# --- START OF NEW LOGGING SETUP ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# --- END OF NEW LOGGING SETUP ---

app = Flask(__name__)

def generate_qr_code(data_string, image_path):
    """Generates a QR code and saves it to the specified path."""
    try:
        qr = qrcode.QRCode(
            version=1,  
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data_string)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        # Use the app's logger
        logger.info(f"Attempting to save QR code to: {image_path}")
        img.save(image_path)
        logger.info(f"Successfully saved QR code to: {image_path}")
        return True
    except DataOverflowError as e:
        # Use the app's logger
        logger.error(f"Error generating QR code: Data too long for QR code. {e}")
        return False
    except Exception as e:
        # Use the app's logger
        logger.error(f"Error saving QR code to {image_path}: {e}")
        return False

def get_qr_code(data_string, idc):
    """Generates and returns a QR code."""
    safe_idc = secure_filename(idc)
    if not safe_idc:
        return jsonify({'error': 'Invalid idc provided'}), 400

    # Ensure the directory exists before trying to save the file
    os.makedirs('./qrcodes', exist_ok=True)
    file_name = f'./qrcodes/qr-{safe_idc}.png'
    
    if generate_qr_code(data_string, file_name):
        # Use the app's logger
        logger.info(f'QR code generated successfully and saved as {file_name}')
        return jsonify({'message': 'QR code generated successfully', 'idc': idc}), 200
    else:
        return jsonify({'error': 'Failed to generate QR code'}), 500

@app.route('/api/v1/qr', methods=['POST'])
def handle_qr_request():
    """Handles the API request for generating QR codes."""
    # Use the app's logger
    logger.info('QR code request received...')
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    procedure = data.get('procedure')
    data_string = data.get('string')
    idc = data.get('idc')

    if not all([procedure, data_string, idc]):
        return jsonify({'error': 'Missing required fields: procedure, string, or idc'}), 400

    # Use the app's logger
    logger.info(f'Procedure: {procedure}')
    logger.info(f'String: {data_string}')
    logger.info(f'IDC: {idc}')

    if procedure == 'get-qr':
        return get_qr_code(data_string, idc)
    else:
        # Use the app's logger
        logger.warning(f'Procedure not found: {procedure}')
        return jsonify({'error': 'Procedure not found'}), 404
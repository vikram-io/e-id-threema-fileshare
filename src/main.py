import os
import sys
import uuid
import json
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from werkzeug.utils import secure_filename
from src.oid4vp.qr_code import generate_qr_code, create_beta_id_auth_request
from src.oid4vp.signature import SwiyuSignatureService
from src.threema_service import ThreemaService

# Set up path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload

# Initialize services
threema_service = ThreemaService()
signature_service = SwiyuSignatureService()

# Store file metadata
files_db = {}

# File database path
FILES_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files_db.json')

# Load file metadata from JSON if exists
if os.path.exists(FILES_DB_PATH):
    try:
        with open(FILES_DB_PATH, 'r') as f:
            files_db = json.load(f)
    except Exception as e:
        logger.error(f"Error loading files database: {e}")

# Custom Jinja2 filter for datetime formatting
@app.template_filter('datetime')
def format_datetime(timestamp):
    """Format a timestamp as a date string"""
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file:
            # Generate a unique ID for the file
            file_id = str(uuid.uuid4())
            
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
            
            # Ensure the upload directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            file.save(file_path)
            
            # Store file metadata
            files_db[file_id] = {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'timestamp': int(datetime.datetime.now().timestamp()),
                'status': 'uploaded',
                'signature': None
            }
            
            # Save the updated files database
            with open(FILES_DB_PATH, 'w') as f:
                json.dump(files_db, f)
            
            return jsonify({'success': True, 'file_id': file_id}), 200
    except Exception as e:
        logger.error(f"Error in upload_file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sign/<file_id>')
def sign_file(file_id):
    # Check if file exists
    if file_id not in files_db:
        return "File not found", 404
    
    file_data = files_db[file_id]
    
    # Get the base URL for callbacks
    base_url = request.url_root.rstrip('/')
    
    # Create authentication request for SWIYU app
    auth_request = create_beta_id_auth_request(file_id, base_url)
    
    # Generate QR code
    qr_code = generate_qr_code(auth_request)
    
    return render_template('sign.html', 
                          file_id=file_id, 
                          file_data=file_data, 
                          qr_code=qr_code,
                          swiyu_url=auth_request)

@app.route('/api/auth-request/<file_id>')
def get_auth_request(file_id):
    """Endpoint to get the authentication request JWT"""
    try:
        # Check if file exists
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        # Get the base URL for callbacks
        base_url = request.url_root.rstrip('/')
        
        # Create a real JWT for the authentication request
        token = signature_service.create_auth_request(file_id, base_url)
        
        return jsonify({'token': token}), 200
    except Exception as e:
        logger.error(f"Error in get_auth_request: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/callback', methods=['POST'])
def auth_callback():
    """Callback endpoint for SWIYU app authentication responses"""
    try:
        # Get the response token from the request
        data = request.json
        if not data or 'vp_token' not in data:
            return jsonify({'error': 'Invalid response'}), 400
        
        response_token = data['vp_token']
        
        # Verify the response
        is_valid, claims = signature_service.verify_auth_response(response_token)
        
        if not is_valid:
            return jsonify({'error': 'Invalid token', 'details': claims}), 400
        
        # Extract the file ID from the request
        # In a real implementation, this would be extracted from the JWT
        # For this POC, we'll extract it from the state parameter
        file_id = data.get('state', '').split('_')[-1]
        
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        # Get the file path
        file_path = files_db[file_id]['path']
        
        # Sign the file
        holder_did = claims.get('sub', 'unknown')
        signature = signature_service.sign_file(file_path, holder_did)
        
        # Update file metadata
        files_db[file_id]['status'] = 'signed'
        files_db[file_id]['signature'] = signature
        files_db[file_id]['signer'] = holder_did
        
        # Save the updated files database
        with open(FILES_DB_PATH, 'w') as f:
            json.dump(files_db, f)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error in auth_callback: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/signature-status/<file_id>')
def signature_status(file_id):
    """Check the signature status of a file"""
    try:
        # Check if file exists
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        # Get the file status
        status = files_db[file_id]['status']
        
        return jsonify({'status': status}), 200
    except Exception as e:
        logger.error(f"Error in signature_status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/share/<file_id>')
def share_file(file_id):
    """Page to share a signed file"""
    # Check if file exists
    if file_id not in files_db:
        return "File not found", 404
    
    file_data = files_db[file_id]
    
    # Check if file is signed
    if file_data['status'] != 'signed':
        return "File is not signed yet", 400
    
    # Get the base URL for sharing
    base_url = request.url_root.rstrip('/')
    verification_url = f"{base_url}/verify/{file_id}"
    
    return render_template('share.html', 
                          file_id=file_id, 
                          file_data=file_data,
                          verification_url=verification_url)

@app.route('/api/send-link/<file_id>', methods=['POST'])
def send_link(file_id):
    """Send a verification link via Threema"""
    try:
        # Check if file exists
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        # Get the Threema ID from the request
        data = request.json
        if not data or 'threema_id' not in data:
            return jsonify({'error': 'Threema ID is required'}), 400
        
        threema_id = data['threema_id']
        
        # Get the base URL for sharing
        base_url = request.url_root.rstrip('/')
        verification_url = f"{base_url}/verify/{file_id}"
        
        # Get the file name
        filename = files_db[file_id]['filename']
        
        # Send the link via Threema
        message = f"You have received a signed file: {filename}. Verify and download it here: {verification_url}"
        result = threema_service.send_message(threema_id, message)
        
        if result['success']:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': result['error']}), 500
    except Exception as e:
        logger.error(f"Error in send_link: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/verify/<file_id>')
def verify_file(file_id):
    """Page to verify and download a signed file"""
    # Check if file exists
    if file_id not in files_db:
        return "File not found", 404
    
    file_data = files_db[file_id]
    
    # Check if file is signed
    if file_data['status'] != 'signed':
        return "File is not signed", 400
    
    # Get the base URL for callbacks
    base_url = request.url_root.rstrip('/')
    
    # Create authentication request for verification
    auth_request = create_beta_id_auth_request(file_id, base_url)
    
    # Generate QR code
    qr_code = generate_qr_code(auth_request)
    
    return render_template('verify.html', 
                          file_id=file_id, 
                          file_data=file_data,
                          qr_code=qr_code,
                          swiyu_url=auth_request)

@app.route('/api/verify-signature/<file_id>', methods=['POST'])
def verify_signature(file_id):
    """Verify a file signature"""
    try:
        # Check if file exists
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        file_data = files_db[file_id]
        
        # Check if file is signed
        if file_data['status'] != 'signed' or not file_data.get('signature'):
            return jsonify({'error': 'File is not signed'}), 400
        
        # Get the file path
        file_path = file_data['path']
        
        # Verify the signature
        is_valid = signature_service.verify_file_signature(file_path, file_data['signature'])
        
        if is_valid:
            return jsonify({'success': True, 'signer': file_data.get('signer', 'unknown')}), 200
        else:
            return jsonify({'error': 'Invalid signature'}), 400
    except Exception as e:
        logger.error(f"Error in verify_signature: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    """Download a file"""
    # Check if file exists
    if file_id not in files_db:
        return "File not found", 404
    
    file_data = files_db[file_id]
    
    # Get the file path
    file_path = file_data['path']
    
    # Send the file
    return send_file(file_path, as_attachment=True, download_name=file_data['filename'])

# Cleanup task for files older than 24 hours
def cleanup_old_files():
    """Remove files older than 24 hours"""
    now = datetime.datetime.now().timestamp()
    files_to_remove = []
    
    for file_id, file_data in files_db.items():
        # Check if file is older than 24 hours
        if now - file_data['timestamp'] > 24 * 60 * 60:
            # Remove the file
            try:
                os.remove(file_data['path'])
                files_to_remove.append(file_id)
            except Exception as e:
                logger.error(f"Error removing file {file_id}: {e}")
    
    # Remove the files from the database
    for file_id in files_to_remove:
        files_db.pop(file_id, None)
    
    # Save the updated files database
    with open(FILES_DB_PATH, 'w') as f:
        json.dump(files_db, f)

# Run cleanup task on startup
cleanup_old_files()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

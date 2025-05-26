import sys
import os
import uuid
import datetime
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
import threading
import time
from src.threema_service import threema_service
from src.oid4vp.service import oid4vp_service
from src.oid4vp.qr_code import generate_qr_code
from src.oid4vp.signature import signature_service

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = set(['*'])  # Allow all file types

# Store file metadata
files_db = {}

# Function to check if a file should be deleted (older than 24 hours)
def is_expired(timestamp):
    now = datetime.datetime.now()
    file_time = datetime.datetime.fromtimestamp(timestamp)
    return (now - file_time).total_seconds() > 86400  # 24 hours in seconds

# Background thread to clean up expired files
def cleanup_expired_files():
    while True:
        try:
            # Check all files in the database
            files_to_delete = []
            for file_id, file_data in files_db.items():
                if is_expired(file_data['timestamp']):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_data['filename'])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    files_to_delete.append(file_id)
            
            # Remove deleted files from the database
            for file_id in files_to_delete:
                del files_db[file_id]
                
            # Save updated database
            save_files_db()
            
        except Exception as e:
            print(f"Error in cleanup thread: {e}")
        
        # Sleep for 1 hour before next cleanup
        time.sleep(3600)

# Save files database to disk
def save_files_db():
    with open(os.path.join(app.config['UPLOAD_FOLDER'], 'files_db.json'), 'w') as f:
        json.dump(files_db, f)

# Load files database from disk
def load_files_db():
    global files_db
    db_path = os.path.join(app.config['UPLOAD_FOLDER'], 'files_db.json')
    if os.path.exists(db_path):
        try:
            with open(db_path, 'r') as f:
                files_db = json.load(f)
        except:
            files_db = {}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file:
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        filename = f"{file_id}_{original_filename}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Store file metadata
        files_db[file_id] = {
            'filename': filename,
            'original_filename': original_filename,
            'timestamp': datetime.datetime.now().timestamp(),
            'size': os.path.getsize(file_path),
            'signed': False,
            'signature': None
        }
        
        # Save updated database
        save_files_db()
        
        # Redirect to signing page
        return redirect(url_for('sign_file', file_id=file_id))
    
    return redirect(url_for('index'))

@app.route('/sign/<file_id>')
def sign_file(file_id):
    if file_id not in files_db:
        flash('File not found')
        return redirect(url_for('index'))
    
    file_data = files_db[file_id]
    return render_template('sign.html', file_id=file_id, file_data=file_data)

@app.route('/api/sign/<file_id>', methods=['POST'])
def api_sign_file(file_id):
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    # Create OID4VP presentation request
    request_data = oid4vp_service.create_presentation_request(file_id)
    
    if not request_data:
        return jsonify({'error': 'Failed to create authentication request'}), 500
    
    # Generate the authorization URL
    auth_url = oid4vp_service.get_auth_url(request_data['jwt'])
    
    # Generate QR code
    qr_code_data = generate_qr_code(auth_url)
    
    # Store request data in session
    files_db[file_id]['auth_request'] = {
        'state': request_data['state'],
        'request_id': request_data['request_id'],
        'created_at': datetime.datetime.now().timestamp()
    }
    
    # Save updated database
    save_files_db()
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'auth_url': auth_url,
        'qr_code': qr_code_data,
        'state': request_data['state']
    })

@app.route('/callback', methods=['POST'])
def oid4vp_callback():
    """Callback endpoint for OID4VP authentication responses"""
    try:
        # Get the presentation JWT and state from the request
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid request format'}), 400
        
        vp_token = data.get('vp_token')
        state = data.get('state')
        
        if not vp_token or not state:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Verify the presentation
        result = oid4vp_service.verify_presentation(vp_token, state)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Verification failed')}), 400
        
        file_id = result['file_id']
        user_did = result['user_did']
        
        if file_id not in files_db:
            return jsonify({'error': 'File not found'}), 404
        
        # Get the file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], files_db[file_id]['filename'])
        
        # Sign the file
        signature_result = signature_service.sign_file(file_path, user_did)
        
        # Update file metadata
        files_db[file_id]['signed'] = True
        files_db[file_id]['signature'] = signature_result['jwt']
        files_db[file_id]['signed_at'] = datetime.datetime.now().timestamp()
        files_db[file_id]['user_did'] = user_did
        files_db[file_id]['file_hash'] = signature_result['file_hash']
        
        # Save updated database
        save_files_db()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'File signed successfully'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/check-signing-status/<file_id>', methods=['GET'])
def check_signing_status(file_id):
    """Check if a file has been signed"""
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    file_data = files_db[file_id]
    
    if file_data.get('signed'):
        # Generate a verification link
        verification_url = url_for('verify_file', 
                                  file_id=file_id, 
                                  signature=file_data['signature'], 
                                  _external=True)
        
        return jsonify({
            'success': True,
            'signed': True,
            'verification_url': verification_url
        })
    else:
        return jsonify({
            'success': True,
            'signed': False
        })

@app.route('/api/send-link/<file_id>', methods=['POST'])
def send_link(file_id):
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    if not files_db[file_id]['signed']:
        return jsonify({'error': 'File not signed yet'}), 400
    
    # Get recipient from request
    data = request.get_json()
    if not data or 'recipient' not in data:
        return jsonify({'error': 'Recipient not provided'}), 400
    
    recipient = data['recipient']
    
    # Generate verification link
    verification_url = url_for('verify_file', 
                              file_id=file_id, 
                              signature=files_db[file_id]['signature'], 
                              _external=True)
    
    # Create message text
    message = f"You've received a signed file: {files_db[file_id]['original_filename']}. Verify and download it here: {verification_url}"
    
    # Send via Threema
    result = threema_service.send_message(recipient, message)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': f'Link sent to {recipient} via Threema',
            'verification_url': verification_url,
            'message_id': result.get('message_id')
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Unknown error sending message')
        }), 500

@app.route('/verify/<file_id>')
def verify_file(file_id):
    if file_id not in files_db:
        flash('File not found')
        return redirect(url_for('index'))
    
    file_data = files_db[file_id]
    signature = request.args.get('signature')
    
    # Check if signature matches
    is_valid = file_data['signed'] and file_data['signature'] == signature
    
    return render_template('verify.html', 
                          file_id=file_id, 
                          file_data=file_data, 
                          is_valid=is_valid,
                          datetime=datetime)

@app.route('/api/unsign/<file_id>', methods=['POST'])
def api_unsign_file(file_id):
    if file_id not in files_db:
        return jsonify({'error': 'File not found'}), 404
    
    signature = request.args.get('signature')
    if not signature or signature != files_db[file_id]['signature']:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # In a real implementation, this would verify the user's E-ID
    # For this PoC, we'll simulate verification
    
    # Record the unsigning action
    files_db[file_id]['unsigned'] = True
    files_db[file_id]['unsigned_at'] = datetime.datetime.now().timestamp()
    
    # Save updated database
    save_files_db()
    
    return jsonify({
        'success': True,
        'file_id': file_id,
        'message': 'File successfully verified and unsigned'
    })

@app.route('/download/<file_id>')
def download_file(file_id):
    if file_id not in files_db:
        abort(404)
    
    file_data = files_db[file_id]
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                              file_data['filename'],
                              as_attachment=True,
                              download_name=file_data['original_filename'])

# Initialize the application
if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Load existing files database
    load_files_db()
    
    # Start cleanup thread
    cleanup_thread = threading.Thread(target=cleanup_expired_files, daemon=True)
    cleanup_thread.start()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)

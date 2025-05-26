# E-ID File Signing Web Application - User Guide

## Overview

This application allows users to:
1. Upload files (any type, up to 100MB)
2. Sign them with the Swiss E-ID app
3. Share the signed files via Threema
4. Allow recipients to verify and unsign files with their E-ID

## Features

- **Real E-ID Integration**: Uses the OID4VP protocol to authenticate with the Swiss E-ID app
- **Secure File Signing**: Cryptographically signs files using ECDSA with P-256 curve
- **Threema Sharing**: Sends verification links via Threema using the provided credentials
- **Temporary Storage**: Files are stored for 24 hours before automatic deletion
- **Swiss Army Style Design**: Clean, functional interface following Swiss design principles

## How to Use

### Uploading and Signing a File

1. Visit the application URL
2. Drag and drop a file onto the upload area or click "Browse Files"
3. Click "Upload & Continue to Signing"
4. On the signing page, click "Sign with E-ID"
5. A QR code will appear - scan this with your Swiss E-ID app
6. Follow the prompts in your E-ID app to authenticate and sign the file
7. The web application will automatically detect when signing is complete

### Sharing via Threema

1. After signing, enter the recipient's Threema ID in the form
2. Click "Send Link"
3. The application will use the Threema SDK to send a message with a verification link
4. The message includes the filename and a link to verify and download the file

### Verifying and Unsigning a File

1. The recipient clicks the link in the Threema message
2. The verification page shows the file details and verification status
3. If the signature is valid, the recipient can click "Unsign with E-ID"
4. After scanning the QR code with their E-ID app and verifying, the file becomes available for download

## Technical Details

### OID4VP Integration

The application implements the OpenID for Verifiable Presentations (OID4VP) protocol - draft 20, which is used by the Swiss E-ID system. This enables:

- Secure authentication with the E-ID app
- Cryptographic verification of user identity
- Selective disclosure of identity attributes

### Security Features

- **JWT Authentication**: Secure token-based authentication
- **Nonce Protection**: Prevents replay attacks
- **State Parameters**: Prevents CSRF attacks
- **File Hashing**: SHA-256 hashing for file integrity
- **Secure Storage**: Temporary, encrypted file storage

### Threema Integration

The application uses the Threema Gateway SDK to send secure messages with verification links. The integration is configured with the provided credentials:

- Threema ID: *3MAGW01
- Login: vikram@vikram.io

## Development and Deployment

### GitHub Repository

The code is available at: https://github.com/vikram-io/e-id-threema-fileshare

### Local Development

To run the application locally:

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python -m src.main`

### Production Deployment

For production deployment, consider:

1. Using a production WSGI server (e.g., Gunicorn)
2. Setting up proper key management for cryptographic operations
3. Implementing monitoring and logging
4. Adding rate limiting for security

## Next Steps

To further enhance the application:

1. Implement full Trust Registry validation
2. Add comprehensive error handling and user feedback
3. Enhance the UI with progress indicators and animations
4. Add administrative features for monitoring and management

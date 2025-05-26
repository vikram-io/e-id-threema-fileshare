# SWIYU App Integration Testing Guide

## Overview

This document provides instructions for testing the E-ID file signing application with the SWIYU app. The application has been fully integrated with the SWIYU beta credentials system, implementing the correct QR code protocol, mobile deep linking, and signature verification flow.

## Prerequisites

- iOS device with the SWIYU app installed
- Access to the deployed application at: https://e-id-file-signing.onrender.com

## Testing Steps

### 1. File Upload and Signing

1. Visit https://e-id-file-signing.onrender.com on your computer or mobile device
2. Upload a file (any type, up to 100MB)
3. On the signing page, you'll see a QR code
4. If on mobile:
   - Tap the QR code to launch the SWIYU app directly
   - Follow the authentication prompts in the app
5. If on desktop:
   - Open the SWIYU app on your iOS device
   - Use the app to scan the QR code
   - Follow the authentication prompts in the app
6. After successful authentication, the file will be signed with your SWIYU beta credentials
7. The application will automatically detect when signing is complete

### 2. Sharing via Threema

1. After signing, you'll be directed to the sharing page
2. Enter a Threema ID to send the verification link
3. Click "Send Link"
4. The recipient will receive a message with a link to verify and download the file

### 3. Verification

1. When the recipient opens the verification link, they'll see the verification page
2. They can verify the signature using their own SWIYU app
3. After verification, they can download the file

## Expected Results

- The QR code should be recognized by the SWIYU app
- Tapping the QR code on mobile should launch the SWIYU app
- The authentication flow should complete successfully
- The file should be properly signed and verifiable
- The Threema sharing should work correctly

## Troubleshooting

If you encounter any issues during testing:

1. **QR Code Not Recognized**: Ensure you're using the latest version of the SWIYU app
2. **Deep Linking Not Working**: Check if your iOS device allows deep linking for the SWIYU app
3. **Authentication Errors**: Verify that your beta credentials are valid and active
4. **Signature Verification Fails**: Check the logs for detailed error information

## Feedback

Please provide detailed feedback on:
1. QR code recognition and scanning experience
2. Deep linking functionality on iOS
3. Authentication flow in the SWIYU app
4. Overall user experience and any suggestions for improvement

Your feedback will help us refine the integration before final deployment.

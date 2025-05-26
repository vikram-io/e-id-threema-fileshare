import qrcode
import io
import base64
from urllib.parse import quote

def generate_qr_code(auth_url, size=300):
    """
    Generate a QR code for SWIYU app authentication
    
    Args:
        auth_url: The authentication URL or payload
        size: Size of the QR code in pixels
        
    Returns:
        Base64 encoded image data
    """
    # For SWIYU app, we need to use the swiyu://oidc protocol instead of swiyu://auth
    # This ensures the QR code is recognized by the SWIYU app
    if not auth_url.startswith('swiyu://'):
        # Encode the URL properly for the SWIYU app
        swiyu_url = f'swiyu://oidc?request_uri={quote(auth_url)}'
    else:
        swiyu_url = auth_url
    
    # Create QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECTION_L,
        box_size=10,
        border=4,
    )
    
    # Add data to the QR code
    qr.add_data(swiyu_url)
    qr.make(fit=True)
    
    # Create an image from the QR code
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image to a bytes buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    
    # Get the image data as base64
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return f"data:image/png;base64,{img_str}"

def create_beta_id_auth_request(file_id, callback_url):
    """
    Create an authentication request for the SWIYU Beta-ID
    
    Args:
        file_id: The ID of the file to be signed
        callback_url: The callback URL for the authentication response
        
    Returns:
        Authentication URL for QR code
    """
    # In a real implementation, this would generate a proper JWT
    # with the correct claims and signature as per the SWIYU documentation
    
    # For the beta environment, we need to use the correct credential type
    # and follow the OID4VP protocol requirements
    
    # This is a simplified version - in production, you would:
    # 1. Generate a proper JWT with the correct headers and claims
    # 2. Sign it with the appropriate key
    # 3. Set up proper callback handling
    
    # For now, we'll create a mock URL that follows the SWIYU protocol format
    auth_url = f"swiyu://oidc?request_uri={callback_url}/api/auth-request/{file_id}"
    
    return auth_url

import qrcode
import io
import base64
import urllib.parse
from PIL import Image

def generate_qr_code(data, size=200):
    """
    Generate a QR code specifically formatted for the SWIYU app
    
    Args:
        data (str): The data to encode in the QR code
        size (int): The size of the QR code in pixels
        
    Returns:
        str: Base64 encoded image data for the QR code
    """
    try:
        # Format the URL specifically for SWIYU app
        # Ensure the URL uses the swiyu:// scheme or is properly formatted for SWIYU
        if data.startswith('http'):
            # Convert standard URL to SWIYU-compatible format
            # Format: swiyu://auth?request_uri=<encoded_url>
            encoded_url = urllib.parse.quote(data)
            swiyu_url = f"swiyu://auth?request_uri={encoded_url}"
        else:
            swiyu_url = data
        
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data to the QR code
        qr.add_data(swiyu_url)
        qr.make(fit=True)
        
        # Create an image from the QR code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize the image if needed
        img = img.resize((size, size))
        
        # Convert the image to base64 for embedding in HTML
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None

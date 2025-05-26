import qrcode
import io
import base64
import urllib.parse
import json
from PIL import Image

def generate_qr_code(data, size=200):
    """
    Generate a QR code specifically formatted for the SWIYU app on iOS
    
    Args:
        data (str): The data to encode in the QR code
        size (int): The size of the QR code in pixels
        
    Returns:
        str: Base64 encoded image data for the QR code and deep link URL
    """
    try:
        # Format the URL specifically for SWIYU app on iOS
        if data.startswith('http'):
            # For iOS, we need to use a specific format that works with the beta app
            # First, encode the URL
            encoded_url = urllib.parse.quote(data)
            
            # Create the SWIYU deep link URL
            # Using both formats to ensure compatibility
            swiyu_url = f"swiyu://oidc?request_uri={encoded_url}"
            
            # Also create a universal link as fallback
            universal_url = f"https://app.swiyu.ch/oidc?request_uri={encoded_url}"
            
            # Store both URLs for the tap-to-launch functionality
            deep_link = {
                "primary": swiyu_url,
                "fallback": universal_url,
                "original": data
            }
        else:
            swiyu_url = data
            deep_link = {
                "primary": data,
                "fallback": data,
                "original": data
            }
        
        # Create QR code instance with higher error correction for better scanning
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction
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
        
        # Return both the image and the deep link data
        return {
            "image": f"data:image/png;base64,{img_str}",
            "deep_link": json.dumps(deep_link)
        }
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return {
            "image": None,
            "deep_link": None
        }

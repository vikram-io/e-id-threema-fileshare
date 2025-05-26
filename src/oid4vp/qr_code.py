import qrcode
import io
import base64
from PIL import Image

def generate_qr_code(data, size=200):
    """
    Generate a QR code for the given data
    
    Args:
        data (str): The data to encode in the QR code
        size (int): The size of the QR code in pixels
        
    Returns:
        str: Base64 encoded image data for the QR code
    """
    try:
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add data to the QR code
        qr.add_data(data)
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

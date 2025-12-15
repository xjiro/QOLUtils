import copykitten
import qrcode
from qreader import QReader
from PIL import Image
import numpy as np


def text_to_qr_clipboard(text):
    """Generate QR code from text and put it in clipboard."""
    print(f"Generating QR code for: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Copy to clipboard
    pixels = img.tobytes()
    copykitten.copy_image(pixels, img.width, img.height)
    
    print(f"QR code ({img.width}x{img.height}) copied to clipboard")


def image_to_text_clipboard(pixels, width, height):
    """Read QR code/barcode from image and put text in clipboard."""
    print(f"Reading QR code from image ({width}x{height})...")
    
    # Convert raw RGBA bytes to PIL Image
    img = Image.frombytes(mode="RGBA", size=(width, height), data=pixels)
    
    # Convert to RGB for qreader
    img_rgb = img.convert('RGB')
    
    # Convert to numpy array for qreader
    img_array = np.array(img_rgb)
    
    # Initialize QReader and decode
    qreader = QReader()
    decoded = qreader.detect_and_decode(image=img_array)
    
    if decoded and len(decoded) > 0:
        # Get first decoded result
        text = decoded[0]
        if text:
            copykitten.copy(text)
            print(f"Decoded text copied to clipboard: {text[:100]}{'...' if len(text) > 100 else ''}")
        else:
            print("No QR code or barcode detected in image")
    else:
        print("No QR code or barcode detected in image")


def process_clipboard():
    """Detect clipboard content and process accordingly."""
    
    # Try to get image first
    try:
        pixels, width, height = copykitten.paste_image()
        # If we got an image, decode it
        image_to_text_clipboard(pixels, width, height)
        return
    except Exception:
        # No image in clipboard, try text
        pass
    
    # Try to get text
    try:
        text = copykitten.paste()
        if text:
            # If we got text, generate QR code
            text_to_qr_clipboard(text)
            return
    except Exception as e:
        print(f"Error reading from clipboard: {e}")
        return
    
    print("No text or image found in clipboard")


if __name__ == "__main__":
    process_clipboard()

from pyzbar.pyzbar import decode
from PIL import Image
import qrcode
import cv2


def scan_qr_code_from_image(image_path):
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)
    decoded_objects = decode(image)

    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            return obj.data.decode('utf-8')

if __name__ == "__main__":
    image_path = "data\\qr_codes\\rdsharma.png"  # Replace with the path to your image file
    result = scan_qr_code_from_image(image_path)
    
    if result:
        print("QR Code Data:", result)
    else:
        print("No QR Code found in the image.")



def generate_qr_code(book_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(book_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f'data\\qr_codes\\{book_id}.png')  # Save the QR code image
# generate_qr_code("rdsharma")

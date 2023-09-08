# import qrcode
# import cv2
# from pyzbar.pyzbar import decode

# def scan_qr_code():
#     cap = cv2.VideoCapture(0)  # Open the default camera (0 or -1)
#     while True:
#         ret, frame = cap.read()
#         decoded_objects = decode(frame)
#         for obj in decoded_objects:
#             if obj.type == 'QRCODE':
#                 return obj.data.decode('utf-8')
#         cv2.imshow("QR Code Scanner", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     cap.release()
#     cv2.destroyAllWindows()
# scan_qr_code()
# # In your book return process, call scan_qr_code() to get the scanned identifier

# def generate_qr_code(book_id):
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(book_id)
#     qr.make(fit=True)

#     img = qr.make_image(fill_color="black", back_color="white")
#     img.save(f'data\\qr_codes\\{book_id}.png')  # Save the QR code image
# # generate_qr_code("rdsharma")














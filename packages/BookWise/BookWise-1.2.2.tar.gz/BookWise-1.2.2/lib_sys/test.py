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



















# Importing necessary modules
import datetime
import pytz
import getpass

# Setting up the timezone
tz = pytz.timezone("Asia/Kolkata")
current_datetime = datetime.datetime.now(tz)
year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second

with open("data\\booklist.txt","r") as f:
   lines= f.readlines()
   books=[line for line in lines]


def delete_line(file_path, line_to_delete):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    new_lines = [line for line in lines if line_to_delete.strip() not in line.strip() ]
    with open(file_path, 'w') as file:
        file.writelines(new_lines)



class student:
   def __init__(self, st_name, st_class):
        self.name = st_name
        self.class_ = st_class

   def borrowbook(self):
        # Function to get a list of books to borrow
        def borrow_booklist():
            input_list = []
            while True:
                item = input(
                    "Enter Name Of The Books To Be Borrowed ( Or Just Click Enter to finish):\t ")
                if item == "":
                    break
                input_list.append(item)
            return input_list

        # Iterate over the list of books to borrow
        for borrow_book in borrow_booklist():
            borrow_book_cleaned = borrow_book.replace(" ", "").lower()
            with open("data\\issue_list.txt", "r") as issue_list:
                line = 0
                while True:
                    line += 1
                    issue_detail = issue_list.readline(line)
                    # Check if the book is available, not already borrowed by the same person and not already borrowed by anyone else
                    issue_detail_cleaned = issue_detail.replace(" ", "").lower()

                    # Check if the book is available, not already borrowed by the same person, and not already borrowed by anyone else
                    if borrow_book_cleaned not in issue_detail_cleaned and self.name.replace(" ", "").lower() not in issue_detail_cleaned and self.class_.replace(" ", "").lower() not in issue_detail_cleaned:
                      for book in books:
                        if borrow_book_cleaned in book.replace(" ", "").lower():
                            folder_path = f"data\\st_borrowed\\{self.name}Of{self.class_}.txt"
                            # Update the student's borrowed book records
                            with open(folder_path, "a") as borrow_lists:
                                borrow_lists.write(borrow_book_cleaned + f"\t ---On{day}/{month}/{year} At({hour}:{minute}:{second})\n")
                            # Update the issue list records
                            with open("data\\issue_list.txt", "a+") as issue_lists:
                                issue_lists.write(borrow_book_cleaned + f"\t By {self.name} Of Class{self.class_}  \t---On{day}/{month}/{year} At({hour}:{minute}:{second})\n")
                            # Remove the borrowed book from the available books list
                            books.remove(borrow_book_cleaned + "\n")
                            
                            # Print issuing information
                            print("You Issued The Book:", borrow_book)
                            print("Please Return The Book Within 30 Days Of Issuing. \n")
                            print(f"If a book is not submitted within 30 days (Before {day}/{month+1}/{year}), a penalty of ₹100 will be charged for each day overdue.\n")
                            # Delete the book from the library's book list
                            delete_line("data\\booklist.txt", borrow_book + "\n")
                            print("Please Keep It Safe.\n")
                            
                            break
                        # Handle case where book is not available
                        elif borrow_book not in (book):
                            print(
                                f"Sorry! The Book You are Searching For ({borrow_book}) Is Currently Unavailable ")
                            break
                    # Handle case where book is already borrowed by the same person or anyone else
                    else:
                        print("Same Person Already Borrowed A Copy Of The Book:", borrow_book)
                        break

        return book

s=student("shaurya","11")
s.borrowbook()
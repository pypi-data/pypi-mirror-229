import datetime
import pytz
# Setting up the timezone
tz = pytz.timezone("Asia/Kolkata")
current_datetime = datetime.datetime.now(tz)
year = current_datetime.year
month = current_datetime.month
day = current_datetime.day
hour = current_datetime.hour
minute = current_datetime.minute
second = current_datetime.second



def delete_line(file_path, line_to_delete):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    new_lines = [line for line in lines if line_to_delete.strip() not in line.strip() ]
    with open(file_path, 'w') as file:
        file.writelines(new_lines)

def append_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data)

def overwrite_file(file_path, lines):
    with open(file_path, 'w') as file:
        file.writelines(lines)

# Class for the library
class Library:
    def __init__(self, available_booklist):
        self.books = available_booklist

    def borrowbook(self, issuer, st_class):
        # Function to get a list of books to borrow
        def borrow_booklist():
            input_list = []
            while True:
                item = input("Enter Name Of The Books To Be Borrowed ( Or Just Click Enter to finish):\t ")
                if item == "":
                    break
                input_list.append(item)
            return input_list
        
        # Loop through books to borrow
        for borrow_book in borrow_booklist():
            
            # Check if the book is available and not already borrowed
            if (borrow_book.lower() +"\n") in (self.books):
                # Create paths for borrower and issue lists
                folder_path = f"data\\st_borrowed\\{issuer}Of{st_class}.txt"
                append_to_file(folder_path,borrow_book+f"\t ---On{day}/{month}/{year} At({hour}:{minute}:{second})\n")
                append_to_file("data\\issue_list.txt",borrow_book+f"\t By {issuer} Of Class{st_class}  \t---On{day}/{month}/{year} At({hour}:{minute}:{second})\n")
                
                self.books.remove(borrow_book+"\n")
                
                # Print issuing information
                print("You Issued The Book:", borrow_book)
                print("Please Return The Book Within A Month. \n")
                print(f"If a book is not submitted within A Month(Before{day}/{month+1}/{year}), a penalty of ₹100 will be charged for each day overdue.\n")
                
                # Delete the book from the book list
                delete_line("data\\booklist.txt", borrow_book+"\n")
                print("Please Keep It Safe.\n")
            else:
                print(f"Sorry! The Book You are Searching For ({borrow_book}) Is Currently Unavailable ")

        return self.books

    def returnbook(self, issuer, st_class):
        # Function to get a list of books to return
        def return_booklist():
            input_list = []
            while True:
                item = input("Enter Name Of The Books To Be Returned ( Or Just Click Enter to finish):\t ")
                if item == "":
                    break
                input_list.append(item)
            return input_list
        
        # Loop through books to return
        for return_book in return_booklist():
            details = f"{return_book}\t By {issuer} Of Class{st_class}"
            
            # Check if the book is borrowed
            with open("data\\issue_list.txt", "r") as issue_list:
                issue_details = issue_list.read()
                if (details) in (issue_details):
                    with open("data\\issue_list.txt", "r") as issue_list:
                        issue_detail = issue_list.readlines()
                    for line in issue_detail:
                        if (details) in line :
                                                      
                            # Delete the book from the borrower's list and issue list
                            folder_path = f"data\\st_borrowed\\{issuer}Of{st_class}.txt"
                            delete_line(folder_path, return_book)
                            delete_line("data\\issue_list.txt", return_book+f"\t By {issuer} Of Class{st_class}  \t---On")
                            print("Thanks For Returning The Book:", return_book)
                            append_to_file("data\\booklist.txt",return_book + "\n")
                            append_to_file("data\\return_list.txt",str(return_book) + f"\t---{day}/{month}/{year}({hour}:{minute}:{second})\n")
                          
                        else:
                            pass
                else:
                    print("Sorry! The Book:", return_book, "Was Never Borrowed.")
        
        return self.books

    def displaybooks(self):
        print("Books Available In Library Are:\n")
        for books_avail in self.books:
            print("\t", books_avail)
        print("\n  -----X-----X-----X-----  \n")

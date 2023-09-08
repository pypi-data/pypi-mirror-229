import getpass
with open("data\\security\\manager.txt","r") as m:
       manager= m.read()     
with open("data\\security\\password.txt","r") as p:
      password= p.read()   
if manager and password:
       manager=manager
       password=password
else:
      from lib_sys.auth_manager import manager,password
   
class   Lib_manager:
    def __init__(self, name):
        self.name = name
    
    # Method to add books to the library
    def add_books(self, add_list):
        # Prompt for password
        passcode = getpass.getpass("Enter Your Password:\t")
        if self.name == manager and passcode == password:
            # Loop through the list of books to be added
            for book in add_list:
                # Append the book to the booklist.txt file
                with open("data\\booklist.txt", "a") as f:
                    f.write(book+"\n")
                print("You Added", book)
        else:
            print("Unauthorized Sign In.")
    
    # Method to display borrow details
    def borrow_details(self):
        # Prompt for password
        passcode = getpass.getpass("Enter Your Password:\t")
        if self.name == manager and passcode == password:
            with open("data\\issue_list.txt", "r") as f:
                details = f.readlines()
                # Check if there are borrow details to display
                if details:
                    for detail in details:
                        if detail != "":
                            print(detail)
                        else:
                            print("ALL THE BOOKS ARE IN THE LIBRARY.")
                else:
                    print("Currently No Book Have Been Issued.")
        else:
            print("Unauthorized Sign In")


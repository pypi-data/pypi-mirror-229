import getpass
 
def authenticate():
    manager = input("Enter Your Name:\t")
    password = ""
    print("The Password Will Be Hidden.")
    print("The Length Of Pssword Must Be Atleast 6. ")
    passid = getpass.getpass("Enter Your Password:\t")
    while True:
        if len(passid)>=6:
          confirm_password = getpass.getpass("Enter Your Password To Confirm:\t")
          if confirm_password == passid:
            password = passid
            with open("data\\security\\manager.txt","w") as m:
                m.write(manager)
            with open("data\\security\\password.txt","w") as p:
              p.write(password)  
            return manager,password
          else:
           print("Try Again!!!\tPasswords Dont Match.")
           
            
        else:
            print("The Length Of Pssword Must Be Atleast 6. ")
            passid = getpass.getpass("Enter Your Password:\t")
        
    
if __name__ == "__main__":
    manager, password = authenticate()
    if manager and password:
        print(f"Authenticated as: {manager}")
        print("Passowrd is :",password)
manager,password=authenticate()
import getpass
  
    
def new_password():
        passcode = getpass.getpass("Enter Your Current Password:\t")
        with open("data\\security\\password.txt","r") as p:
          password= p.read() 
        yes=["yes","yess","ye","ys","y"]
        if passcode == password:
            confirm=input("Are You Sure You Want To Change The Password.(Y/N):\t")
            if confirm.lower() in yes:
                password = ""
                print("The Password Will Be Hidden.")
                print("The Length Of Pssword Must Be Atleast 6. ")
                passid = getpass.getpass("Enter Your New Password:\t")
                while True:
                    if len(passid)>=6:
                        confirm_password = getpass.getpass("Confirm Your New Password:\t")
                        if confirm_password == passid:
                          password = passid
                          with open("data\\security\\password.txt","w") as p:
                            p.write(password)  
                          return password
                        else:
                          print("Try Again!!!\tPasswords Dont Match.")
                    else:
                        print("The Length Of Pssword Must Be Atleast 6. ")
                        passid = getpass.getpass("Enter Your Password:\t")
                    
            else:
                print("No Change In Password.")    

password=new_password()                
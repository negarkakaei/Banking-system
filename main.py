import datetime

from server import Server, Data, Account


def menu(ac_type):
    while True:
        print("please choose one the actions below.")
        if ac_type == "employee":

            option = input("1. update balances\n2. interest payment\n-> ")
            if option == '1':
                status = myServer.execute("update_balances", None)
            elif option == '2':
                status = myServer.execute("interest_payment", None)
            elif option == '0':
                break

        elif ac_type == "client":

            option = input("1. deposit\n2. withdraw\n3. transfer\n4. check balance\n-> ")
            if option == '1':
                amount = input("please enter the amount of deposit -> ")
                status = myServer.execute("deposit", Data(None, None, amount, None))

            elif option == '2':
                amount = input("please enter the amount of withdraw -> ")
                status = myServer.execute("withdraw", Data(None, None, amount, None))

            elif option == '3':
                amount = input("please enter the amount of transfer -> ")
                accountNum = input("please enter the account number for transfer -> ")
                while True:
                    if len(accountNum) != 16:
                        accountNum = input("account number must be 16 digits. try again -> ")
                    else:
                        break
                status = myServer.execute("transfer", Data(None, None, amount, accountNum))

            elif option == '4':
                status = myServer.execute("check_balance", None)

            elif option == '0':
                break

        if status[-1] == 1 and type == 'client':
            print("operation successful")
        else:
            print("operation failed. try again!")



def start():
    while True:
        option = input("1. login\n2. signup\n-> ")

        if option == '1':
            username = input("username-> ")
            password = input("password-> ")
            data = Data(username, password, None, None)
            status = myServer.execute("login", data)
            # find out what type of account it is and show menu
            if status[-1] != 1:
                print("wrong username or password")
            elif status[-1] == 1:
                menu(status[7])

        elif option == '2':
            print("please fill the registration form below\n")
            firstName = input("firstName-> ")
            lastName = input("lastName-> ")
            nationalID = input("nationalID-> ")
            birth = input("birth(yyyy:mm:dd)-> ")
            password = input("please choose a strong password-> ")
            option = input("please choose the type of the account you would like to register for\n"
                           "1. employee    2. client\n-> ")
            interest = None
            ac_type = None
            if option == '1':
                interest = 0
                ac_type = 'employee'
            if option == '2':
                interest = input("please type your preferred interest rate-> ")
                ac_type = 'client'

            account = Account(None, firstName, lastName, None, nationalID, interest,
                              datetime.datetime.strptime(birth, "%Y:%m:%d"), password, ac_type)
            # if registration is accepted from server status becomes true
            status = myServer.execute("register", account)
            if status[-1] == 1:
                print("thank you. your registration is complete\n")
                data = Data(myServer.fetchUsername(), password, None, None)
                myServer.execute("login", data)
                menu(ac_type)
            else:
                print("registration failed. please try again.\n")
                break

        elif option == '0':
            break


if __name__ == '__main__':
    myServer = Server()
    myServer.start()
    start()

import datetime

import mysql.connector
from datetime import date


class Server:
    db = mysql.connector.connect(host="localhost", user="root", password="NegarSQL123456")
    cursor = db.cursor(buffered=True)
    current_username = None
    balance_amount = 0
    accountNumber = None

    def fetchUsername(self):
        return self.current_username

    def execute(self, key, data) -> bool:
        status = None
        result = None
        if key == "register":

            if (datetime.datetime.today() - data.birth).days >= 13 * 365:

                self.cursor.execute("SELECT MAX(accountNumber) FROM accounts ")
                result = self.cursor.fetchone()
                self.accountNumber = int(result[0]) + 1

                result = self.cursor.callproc("register", (data.nationalID, data.birth, self.accountNumber, data.lastName,
                                                           data.firstName, data.password, data.interestRate, data.type,
                                                           status))

            else:
                result[-1] = 0

        elif key == "login":
            result = self.cursor.callproc("login", (data.username, data.password, status))
            Server.db.commit()

            if result[-1] == 1:
                self.current_username = data.username

        elif key == "deposit":
            result = self.cursor.callproc("deposit", (data.amount, self.accountNumber, status))
            Server.db.commit()

        elif key == "withdraw":
            result = self.cursor.callproc("withdraw", (data.amount, self.accountNumber, status))
            Server.db.commit()

        elif key == "transfer":
            result = self.cursor.callproc("transfer", (data.amount, data.accountNum, self.accountNumber, status))
            Server.db.commit()

        elif key == "interest_payment":
            result = self.cursor.callproc("update_balances")
            Server.db.commit()
            result = self.cursor.callproc("interest_payment")
            Server.db.commit()

        elif key == "update_balances":
            result = self.cursor.callproc("update_balances")
            Server.db.commit()

        elif key == "check_balance":
            result = self.cursor.callproc("update_balances")
            Server.db.commit()
            result = self.cursor.callproc("check_balance", self.current_username, Server.balance_amount)
            Server.db.commit()

        return result

    # to be called at the beginning of the main program
    def start(self):

        self.cursor.execute("CREATE DATABASE IF NOT EXISTS banking_db")
        self.db.connect(database="banking_db")

        self.cursor.execute("DROP TRIGGER IF EXISTS banking_db.username_creation")
        self.cursor.execute("CREATE TRIGGER username_creation BEFORE INSERT ON accounts FOR EACH ROW "
                            "BEGIN "
                            "   SET NEW.username = CONCAT(NEW.firstName, '', NEW.lastName);"
                            "END ")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.register ")
        self.cursor.execute("CREATE PROCEDURE register(IN nationalID char(10), IN birth date, IN accountNum char(16),"
                            "IN lastName varchar(10), IN firstName varchar(10), IN password varchar(20), "
                            "IN interest_rate float, IN ac_type varchar(10),  OUT status boolean) "
                            "BEGIN "
                            "DECLARE res2 boolean; "
                            "DECLARE res1 boolean; "

                            "INSERT INTO accounts(username, password, firstName, lastName, nationalID, birthDate, "
                            "accountType, interest_rate, date_created, accountNumber) "
                            "VALUES (null, SHA2(password, 256), firstName, lastName, nationalID, birth,"
                            " ac_type, interest_rate,current_date, accountNum); "
                            "IF ROW_COUNT() > 0 THEN SET res1 = TRUE; END IF; "

                            "INSERT INTO last_balances(account, amount) VALUES (accountNum, 0); "
                            "IF ROW_COUNT() > 0 THEN SET res2 = TRUE; END IF; "
                            "SET status = res1 AND res2; "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.login ")
        self.cursor.execute("CREATE PROCEDURE login(IN username varchar(20), IN password varchar(20),"
                            "OUT status boolean)"
                            "BEGIN "
                            "   DECLARE hashed_password blob; "
                            "   SELECT password INTO hashed_password "
                            "   FROM accounts "
                            "   WHERE accounts.username = username; "

                            "   IF hashed_password = SHA2(password, 256) THEN "
                            "       INSERT INTO login_log (username, login_time) "
                            "       VALUES (username, CURRENT_TIME); "
                            "       SET status = TRUE; "
                            "   ELSE "
                            "       SET status = FALSE; "
                            "   END IF; "
                            "END ")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.deposit ")
        self.cursor.execute("CREATE PROCEDURE deposit(IN amount decimal(10,4), IN currentUser char(16), "
                            "OUT status boolean) "
                            "BEGIN "
                            "   INSERT INTO transactions(`type`, `time`, `from`, `to`, amount) VALUES ('deposit', "
                            "   current_time, null, currentUser, amount); "
                            "   SET status = TRUE; "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.withdraw ")
        self.cursor.execute("CREATE PROCEDURE withdraw(IN amount decimal(10,4), IN currentUser char(16),"
                            "OUT status boolean) "
                            "BEGIN "
                            "   INSERT INTO transactions(`type`, `time`, `from`, `to`, amount) VALUES ('withdraw', "
                            "   current_time, currentUser, null, amount); "
                            "   SET status = TRUE; "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.transfer ")
        self.cursor.execute("CREATE PROCEDURE transfer(IN amount decimal(10,4), IN accountNum char(16), "
                            "IN currentUser char(16), OUT status boolean) "
                            "BEGIN "
                            "   CASE WHEN accountNum IN (SELECT accountNumber "
                            "                            FROM accounts) THEN "
                            "           INSERT INTO transactions(`type`, `time`, `from`, `to`, amount) VALUES "
                            "           ('transfer', current_time, currentUser, accountNum, amount); "
                            "           SET status = TRUE; "
                            "       ELSE "
                            "           SET status = FALSE; "
                            "   END CASE; "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.interest_payment ")
        self.cursor.execute("CREATE PROCEDURE interest_payment() "
                            "BEGIN "
                            "   INSERT INTO transactions (`type`, `time`, `from`, `to`, `amount`) "
                            "   SELECT 'interest', CURRENT_TIME, NULL, accountNumber, interest_rate * amount "
                            "   FROM accounts NATURAL JOIN last_balances; "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.update_balances ")
        self.cursor.execute("CREATE PROCEDURE update_balances() "
                            "BEGIN "
                            "END")

        self.cursor.execute("DROP PROCEDURE IF EXISTS banking_db.check_balance ")
        self.cursor.execute("CREATE PROCEDURE check_balance(IN username varchar(20), OUT balance decimal(10,4)) "
                            "BEGIN "
                            "   SELECT amount INTO balance "
                            "   FROM accounts NATURAL JOIN last_balances "
                            "   WHERE accounts.username = username; "
                            "END")


class Account:

    # class constructor
    def __init__(self, username, firstName, lastName, accountNum, nationalID, interestRate, birth, password, type):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.accountNum = accountNum
        self.nationalID = nationalID
        self.interestRate = interestRate
        self.birth = birth
        self.password = password
        self.type = type

    def hash_password(self, password):
        pass


class Data:
    def __init__(self, username, password, amount, accountNum):
        self.username = username
        self.password = password
        self.amount = amount
        self.accountNum = accountNum

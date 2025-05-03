    import os
    import sqlite3

    # From: https://goo.gl/YzypOI
    def singleton(cls):
        instances = {}

        def getinstance():
            if cls not in instances:
                instances[cls] = cls()
            return instances[cls]

        return getinstance


    class DatabaseDriver(object):
        """
        Database driver for the Task app.
        Handles with reading and writing data with the database.
        """

        def __init__(self):
            self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
            self.conn.execute("PRAGMA foreign_keys = ON;")
            self.create_user_table()
            self.create_transaction_table()

        def create_user_table(self):
            """
            Using SQL to create a user table
            """
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            userid TEXT UNIQUE NOT NULL,
                            name TEXT NOT NULL, 
                            username TEXT NOT NULL,
                            balance DOUBLE NOT NULL,
                            initial_balance DOUBLE NOT NULL DEFAULT 0,
                            password TEXT NOT NULL
                                );
            """
            )
        def create_transaction_table(self):
            self.conn.execute("""CREATE TABLE IF NOT EXISTS transaction (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_name TEXT NOT NULL,
        sender_id TEXT NOT NULL,
        receiver_id TEXT NOT NULL,
        amount DOUBLE NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL,
        FOREIGN KEY (sender_id) REFERENCES user(userid),
        FOREIGN KEY (receiver_id) REFERENCES user(userid)
    );
    """)
        def insert_transaction(self, transaction_name, sender_id, receiver_id, amount, category):
            """
            Insert a transaction record
            """
            cursor = self.conn.execute("""
                INSERT INTO transaction (transaction_name, sender_id, receiver_id, amount, category)
                VALUES (?, ?, ?, ?);
            """, (transaction_name, sender_id, receiver_id, amount, category))
            self.conn.commit()
            return cursor.lastrowid
        def get_all_user_transactions(self,userid):
            """
            Get all transactions from the transaction table
            """
            cursor = self.conn.execute("SELECT * FROM transaction WHERE sender_id = ? OR receiver_id = ?;", (userid, userid))
            transactions = []
            for row in cursor:
                transactions.append({
                    "id": row[0],
                    "transaction_name": row[1],
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "timestamp": row[5],
                    "category": row[6]
                })
            return transactions
        def get_transactions_by_category_and_userid(self,userid,category):
            """
            Get all transactions by category and user id
            """
            cursor = self.conn.execute("SELECT * FROM transaction WHERE (sender_id = ? OR receiver_id = ?) AND category = ?;", (userid, userid, category))
            transactions = []
            for row in cursor:
                transactions.append({
                    "id": row[0],
                    "transaction_name": row[1],
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "timestamp": row[5],
                    "category": row[6]
                })
            return transactions
        def get_userid_by_username(self,username):
            """
            Get the userid by username
            """
            cursor = self.conn.execute("SELECT userid FROM user WHERE username = ?;", (username,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        def get_id_by_userid(self,userid):
            """
            Get the userid by id
            """
            cursor = self.conn.execute("SELECT id FROM user WHERE userid = ?;", (userid,))
            row = cursor.fetchone()
            if row:
                return row[0]
            return None
        def delete_user_table(self):
            """
            Deleting user table using SQL
            """
            self.conn.execute("DROP TABLE IF EXISTS user;")
            self.conn.commit()
        def get_all_users(self):
            """
            Using SQL, returns all users in table
            """
            cursor = self.conn.execute("SELECT * FROM user;") #how to run a SQL query 
            users = []
            for row in cursor: 
                users.append({"userid": row[1] , "name": row[2], "username": row[3]})
            return users
        
        def get_user_by_id(self, userid):
            """
            Using SQL, getting a user by id
            """
            cursor = self.conn.execute("SELECT * FROM user WHERE userid = ?;", (userid,))
            for row in cursor:
                return {"id": row[0], "name": row[2], "username": row[3], "balance": row[4]}
            return None 
        
        def insert_user_table(self, name, username, password, balance=0, initial_balance=0):
            """
            Using SQL, insert user into user table
            """
            userid = os.urandom(32).hex() #generate a random 32 byte string and convert it to hex
            cursor = self.conn.execute("INSERT INTO user (name, username, balance,userid, initial_balance, password) VALUES (?, ?, ?, ?, ?, ?);", (name, username, balance,userid, initial_balance, password))
            self.conn.commit() #commits the changes we made to the table (because we made a change to the data)
            #returns the id of the row we just created
            return cursor.lastrowid

        
        def delete_user_by_id(self, id):
            """
            Using SQL, delete user by id
            """
            self.conn.execute("DELETE FROM user WHERE id = ?;", (id,))
            self.conn.commit()

        def update_user_by_id(self, balance, id):
                """
                Using SQL, update a user by id
                """
                self.conn.execute("UPDATE user SET balance = ? WHERE id = ?;", (balance, id))
                #whenever changing something have to commit but not when reading something 
                self.conn.commit()
        def update_user_initial_balance_by_id(self, initial_balance, id):
                """
                Using SQL, update a user by id
                """
                self.conn.execute("UPDATE user SET initial_balance = ? WHERE id = ?;", (initial_balance, id))
                #whenever changing something have to commit but not when reading something 
                self.conn.commit()
        def get_user_password_by_id(self, id):
            """
            Using SQL, get user password by id
            """
            cursor = self.conn.execute("SELECT password FROM user WHERE id = ?;", (id,))
            for row in cursor:
                return row[0]
            return None
    # Only <=1 instance of the database driver
    # exists within the app at all times
    DatabaseDriver = singleton(DatabaseDriver)

import json
from flask import Flask, request
import db
import copy

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello world!"

users = {
    1: {
        "id": 1,
        "name": "Conner",
        "username": "cswenberg",
        "balance": 24
    },
    2: {
        "id": 2,
        "name": "Alicia",
        "username": "aawang",
        "balance": 25
    }
}
user_id_counter = 3

# your routes here

# Get all users
@app.route("/api/users/", methods=["GET"])
def get_all_users():
    """
    Get all users
    User is defined as someone who creates an account.
    """
    return json.dumps({"users": DB.get_all_users()}), 200

# Create a user
@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Create a new user with name, username, and balance - not done by default
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Something went wrong creating the user"}), 400
    return json.dumps(user), 201
    



# Get user by ID
@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_user_by_id(user_id):
    """
    Gets a user with given id with name, username, and balance - not done by default
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User is not found!"}), 404
    return json.dumps(user), 200


# Delete user 
@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Deletes a given user by id 
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User is not found"}), 404 
    DB.delete_user_by_id(user_id)
    return json.dumps(user), 200


# Send money from one user to another 
@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Transfers money from one user to another user by updating the balance
    """
    body = json.loads(request.data)
    sender_id = body["sender_id"]
    print(sender_id)
    receiver_id = body["receiver_id"]
    amount = body["amount"]
    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)
    if sender is None:
        return json.dumps({"error": "Sender is none"}), 400
    if receiver is None:
        return json.dumps({"error": "receiver is none"}), 400
    if amount is None:
        return json.dumps({"error": "amount is none"}), 400
    if amount > sender.get("balance"):
        return json.dumps({"error": "Insufficient funds to complete send request"}), 400
    DB.update_user_by_id(sender.get("balance")-amount, sender_id)
    DB.update_user_by_id(receiver.get("balance")+amount, receiver_id)
    return json.dumps(body), 200



#new methods
# Get total amount 

"""

Request:


"""
@app.route("/api/user/<int:user_id>/", methods=["GET"])
def get_total_amount(user_id):
    """
    Gets total amount of money
    """
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User is not found!"}), 404
    body = json.loads(request.data)
    amount = body["amount"]
    return json.dumps(body), 200


@app.route("/api/subtract/", methods=["POST"])
def subtract_expenses():
    """
    Subtracts expenses from total
    """
    body = json.loads(request.data)
    expense = body["expense"]
    user_id = body["user_id"]
    amount = body["amount"]
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "receiver is none"}), 400
    if amount is None:
        return json.dumps({"error": "amount is none"}), 400
    DB.update_user_by_id(user.get("balance")-amount, user)
    return json.dumps(body), 200


@app.route("/api/subtract/", methods=["POST"])
def add_salary():
    """
    Subtracts expenses from total
    """
    body = json.loads(request.data)
    salary = body["expense"]
    user_id = body["user_id"]
    amount = body["amount"]
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "receiver is none"}), 400
    if amount is None:
        return json.dumps({"error": "amount is none"}), 400
    DB.update_user_by_id(user.get("balance")+amount, user)
    return json.dumps(body), 200









if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000, debug=True)

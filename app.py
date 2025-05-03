import json
from flask import Flask, request
import db as db
import os
import hashlib
from dotenv import load_dotenv
load_dotenv()
DB = db.DatabaseDriver()
app = Flask(__name__)

from flask import jsonify
salt  = os.getenv("PASSWORD_SALT")
times = int(os.getenv("NUMBER_OF_ITERATIONS"))
def sha256_with_salt(password, salt):
    #iteratively hash the password with sha256 using salt from .env
    temp = password
    for i in range(times):
        combined = (temp + salt).encode('utf-8')
        hash = hashlib.sha256(combined).hexdigest()
        temp = hash
    return hash
def success_response(body, code=200):
    #simplify returning success responses
    return jsonify(body), code
def failure_response(message, code=404):
    #simplify returning failure responses
    return jsonify({'error': message}), code
categories = ["Housing", "Insurance", "Food", "Savings", "Transportation", "Personal", "Recreation", "Utilities", "Giving", "Other"]
percentages = [0.25, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.01]
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
@app.route("/api/users/", methods=["GET","POST"])
def extra_users():
    #(optional) Getting all users (without balances) and user creation with password and hashing
    if request.method == 'GET':
        #Returns all users in table
        return success_response({"users":DB.get_all_user()})
    if request.method == 'POST':
        #Creating user with name,username,balance, and password enforced
        body = json.loads(request.data)
        name = body.get("name")
        username = body.get("username")
        balance = body.get("balance", 0)
        password = body.get("password")
        if "name" not in body or not body["name"].strip():
            return failure_response("Missing or empty 'name'",404)
        if "username" not in body or not body["username"].strip():
            return failure_response("Missing or empty 'username'",404)
        if "password" not in body or not body["password"].strip():
            return failure_response("Unauthorized",401)
        user_id= DB.insert_user_table(name,username,sha256_with_salt(password,salt),balance)
        user = DB.get_user_by_id(user_id)
        if user is None:
            return failure_response("Something went wrong", 500)
# Get user by ID
@app.route("/api/user/<int:id>/", methods=["POST","DELETE"])
def extra_users_by_id(id):
    #Getting with authorization and deleting users (is it supposed to be unauthorized?)
    if request.method == 'POST':
        #Getting user by id and requiring that user's password 
        body = json.loads(request.data)
        password = body.get("password")
        if DB.get_user_by_id(id) is None:
            return failure_response("No user found",404)
        if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
            return failure_response("Unauthorized", 401)
        
        return success_response(DB.get_user_by_id(id),200)
    if request.method == 'DELETE':
        #Delete user by id
        if DB.get_user_by_id(id) is None:
            return failure_response("No user found",404)
        if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
            return failure_response("Unauthorized", 401)
        temp_user= DB.get_user_by_id(id)
        DB.delete_user_by_id(id)
        return success_response(temp_user,200)

# Send money from one user to another 
@app.route("/api/send/", methods=["POST"])
def send_money():
    """
    Transfers money from one user to another user by updating the balance
    """
    body = json.loads(request.data)
    sender_username = body["sender_username"]
    receiver_username = body["receiver_username"]
    sender_id = DB.get_userid_by_username(sender_username)
    receiver_id = DB.get_userid_by_username(receiver_username)
    amount = body["amount"]
    if sender_id is None:
        return json.dumps({"error": "Sender is none"}), 400
    if receiver_id is None:
        return json.dumps({"error": "receiver is none"}), 400
    if amount is None:
        return json.dumps({"error": "amount is none"}), 400
    if amount > sender_id.get("balance"):
        return json.dumps({"error": "Insufficient funds to complete send request"}), 400
    DB.update_user_by_id(sender_id.get("balance")-amount, sender_id)
    DB.update_user_by_id(receiver_id.get("balance")+amount, receiver_id)
    return json.dumps(body), 200

@app.route("/api/budgeting/simple/<int:id>/", methods=["POST"])
def budgetting_simple(id):
    """
    50/30/20 budgeting
    """
    body = json.loads(request.data)
    password = body["password"]
    if DB.get_user_by_id(id) is None:
        return failure_response("No user found",404)
    if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
        return failure_response("Unauthorized", 401)
    balance = DB.get_user_by_id(id).get("balance")
    return json.dumps({"needs": int(balance*0.5),"wants":int(balance*0.3),"savings":int(balance*0.2)}), 200
@app.route("/api/budgeting/advanced/<string:userid>/", methods=["POST"])
def budgetting_advanced(userid):
    id = DB.get_id_by_userid(userid)
    initial_balance = DB.get_user_by_id(id).get("initial_balance")
    """
    Advanced budgeting
    """
    body = json.loads(request.data)
    password = body["password"]
    if DB.get_user_by_id(id) is None:
        return failure_response("No user found",404)
    if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
        return failure_response("Unauthorized", 401)
    balance = DB.get_user_by_id(id).get("balance")
    return json.dumps({"Housing (25-30%)": str(int(initial_balance*0.25))+"to"+str(int(initial_balance*0.30)),"Insurance (10-20%)":str(int(initial_balance*0.1))+"to"+str(int(initial_balance*0.20)),
                       "Food (10-15%)":str(int(initial_balance*0.10))+"to"+str(int(initial_balance*0.15)),"Savings (10-15%)":str(int(initial_balance*0.10))+"to"+str(int(initial_balance*0.15)),"Transportation (10-15%)":str(int(initial_balance*0.10))+"to"+str(int(initial_balance*0.15)),
                       "Personal (5-10%)":str(int(initial_balance*0.05))+"to"+str(int(initial_balance*0.10)), "Recreation (5-10%)":str(int(initial_balance*0.05))+"to"+str(int(initial_balance*0.10)), "Utilities (5-10%)":str(int(initial_balance*0.05))+"to"+str(int(initial_balance*0.10)),"Giving (1-5%)":str(int(initial_balance*0.01))+"to"+str(int(initial_balance*0.05))}), 200

@app.route("/api/transactions/", methods=["POST"])
def transactions():
    """
    Creates a transaction and adds it to the database
    """
    body = json.loads(request.data)
    sender_username = body["sender_username"]
    receiver_username = body["receiver_username"]
    transaction_name = body["transaction_name"]
    sender_id = DB.get_userid_by_username(sender_username)
    receiver_id = DB.get_userid_by_username(receiver_username)
    amount = body["amount"]
    category = body["category"]
    if sender_id is None:
        return json.dumps({"error": "No sender exists"}), 400
    if receiver_id is None:
        return json.dumps({"error": "No receiver exists"}), 400
    if amount is None:
        return json.dumps({"error": "amount is none"}), 400
    if transaction_name is None:
        return json.dumps({"error": "transaction name needed"}), 400
    if category is None or category not in ["Housing", "Insurance", "Food", "Savings", "Transportation", "Personal", "Recreation", "Utilities", "Giving", "Other"]:
        return json.dumps({"error": "category is none or not in list"}), 400
    DB.insert_transaction(sender_id, receiver_id, amount, category)
    return json.dumps(body), 200
@app.route("/api/set-initial-balance/<string:userid>", methods=["POST"])
def set_initial_balance(userid):
    global initial_balance
    body = json.loads(request.data)
    password = body["password"]
    balance = body.get("initial_balance")
    id = DB.get_id_by_userid(userid)
    if DB.get_user_by_id(id) is None:
        return failure_response("No user found",404)
    if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
        return failure_response("Unauthorized", 401)
    if balance is None:
        return failure_response("initial_balance is required", 400)
    try:
        initial_balance = float(balance)
    except ValueError:
        return failure_response("initial_balance must be a number", 400)
    if initial_balance < 0:
        return failure_response("initial_balance must be a positive number", 400)
    if initial_balance is None:
        return failure_response("initial_balance is required", 400)
    DB.update_user_initial_balance_by_id(id, initial_balance)
    return success_response({"message": f"Initial balance set to {initial_balance}"}, 200)

    
    
    return success_response({"message": f"Initial balance set to {initial_balance}"}, 200)
@app.route("/api/transactions/<string:userid>/", methods=["GET"])
def get_transactions_by_user_id(userid):
    """
    Gets all transactions by user id
    """
    body = json.loads(request.data)
    password = body["password"]
    id = DB.get_id_by_userid(userid)
    if DB.get_user_by_id(id) is None:
        return failure_response("No user found",404)
    if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
        return failure_response("Unauthorized", 401)
    transactions = DB.get_all_user_transactions(id)
    return json.dumps(transactions), 200

@app.route("/api/transactions/<string:userid>/<string:category>/", methods=["GET"])
def get_transactions_by_category_and_user_id(userid, category):
    """
    Gets all transactions by user id and category
    """
    id = DB.get_userid_by_user(userid)
    body = json.loads(request.data)
    password = body["password"]
    if DB.get_user_by_id(id) is None:
        return failure_response("No user found",404)
    if sha256_with_salt(password,salt) != DB.get_user_password(id)[0]:
        return failure_response("Unauthorized", 401)
    transactions = DB.get_transactions_by_category_and_userid(userid, category)
    return json.dumps(transactions), 200
@app.route("/api/budgeting/tracking/<string:userid>", methods=["GET"])
def get_budgeting_tracking(userid):
    """
    Gets all transactions by user id and returns all categories where budget was exceeded, including by how much.
    """
    global categories
    id = DB.get_id_by_userid(userid)
    initial_balance = DB.get_user_by_id(id).get("initial_balance")
    global percentages  # assuming percentages aligns with categories

    exceeded_categories = []

    for i in range(len(categories)-1):
        transactions = DB.get_transactions_by_category_and_userid(userid, categories[i])
        tot = 0
        for transaction in transactions:
            if userid == transaction.get("sender_id"):
                tot += transaction.get("amount")
            elif userid == transaction.get("receiver_id"):
                tot -= transaction.get("amount")
        
        allowed_budget = initial_balance * percentages[i]
        
        if tot > allowed_budget:
            exceeded_amount = tot - allowed_budget
            exceeded_amount_rounded = round(exceeded_amount, 2)
            exceeded_categories.append({
                "category": categories[i],
                "exceeded_amount": exceeded_amount_rounded,
                "allowed_budget": round(allowed_budget, 2),
                "total_spent": round(tot, 2),
                "message": f"Budget exceeded for {categories[i]} by ${exceeded_amount_rounded}"
            })

    if exceeded_categories:
        return json.dumps({
            "message": "Budget exceeded for some categories",
            "exceeded_categories": exceeded_categories
        }), 200
    else:
        return json.dumps({
            "message": "No budget exceeded in any category"
        }), 200



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
    app.run(host="0.0.0.0", port=5000, debug=True)

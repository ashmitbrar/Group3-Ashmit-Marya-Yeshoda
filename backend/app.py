from flask import Flask, session, flash, redirect, url_for, request, render_template, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__, static_folder='../Frontend/static', template_folder='../Frontend/templates')
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/add_investment')
def add_investment():
    return render_template('add_investment.html')

@app.route('/add_debt')
def add_debt():
    # Ensure the user is logged in before allowing them to add a debt
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('debts.html')

@app.route('/add_budget')
def add_budget():
    return render_template('budgets.html')

@app.route('/add_transaction')
def add_transaction():
    # Ensure the user is logged in before allowing them to add a transaction
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('transactions.html')

@app.route('/add_expense')
def add_expense():
    # Your logic here
    return render_template('add_expense.html')

@app.route('/add_savings_goal')
def add_savings_goal():
    # Ensure the user is logged in before allowing them to add a savings goal
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('savings_goals.html')

@app.route('/splitting')
def splitting():
    # Add your logic here for what should happen when this page is accessed.
    return render_template('splitting.html')

@app.route('/account')
def account_page():
    return render_template('account.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    

    data = read_data()

    # Assuming 'user_id' in session is an int
    user_id = session['user_id']

    # Finding the logged-in user's data
    user_data = next((user for user in data['users'] if user['user_id'] == user_id), None)
    if not user_data:
        return jsonify({"message": "User not found"}), 404

    # Collecting all related data for the user
    user_transactions = [t for t in data['transactions'] if t['user_id'] == user_id]
    user_recurring_expenses = [re for re in data['recurring_expenses'] if re['user_id'] == user_id]
    # ... continue collecting data as per your existing code ...
# Check if there are any split details in the session
    split_details = session.pop('split_details', None)
    # Constructing the dashboard data
    dashboard_data = {
        "user_info": user_data,  # assuming user_data contains all necessary user info
        "transactions": user_transactions,
       "recurring_expenses": user_recurring_expenses,
        "split_details": split_details  # Pass the split details to the template
    }

    return render_template('dashboard.html', dashboard_data=dashboard_data)


DATA_FILE = 'data.json'

def read_data():
    if not os.path.exists(DATA_FILE):
        return {
            "users": [],
            "transactions": [],
            "recurring_expenses": [],
            "notifications": [],
            "debts": [],
            "investments": [],
            "budgets": [],
            "savings_goals": [],
            "currencies": [],
            "user_settings": [],
            "categories": [],
            "groups": [],
            "group_balances": [],
            "expenses": [],
            "group_expenses": []
        }
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


# user management
# Route to register a new user
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json

    # Check for missing data
    if not all(key in user_data for key in ['username', 'email', 'password']):
        return jsonify({"error": "Missing data"}), 400

    data = read_data()

    # Check for existing username or email
    existing_user = next((u for u in data['users'] if u['username'] == user_data['username'] or u['email'] == user_data['email']), None)
    if existing_user:
        return jsonify({"error": "User already exists"}), 409

    user_data['password_hash'] = generate_password_hash(user_data['password'])
    del user_data['password']  # Remove the plain password from the data

    user_data['user_id'] = len(data['users']) + 1  # Assign a new user ID

    data['users'].append(user_data)  # Add the new user to the 'users' list
    write_data(data)  # Write the updated data back to the file
    return jsonify({"message": "User registered successfully", "user_id": user_data['user_id']}), 201

@app.route('/login', methods=['POST'])
def login():
    credentials = request.json
    username = credentials['username']
    password = credentials['password']
    data = read_data()

    user = next((u for u in data['users'] if u['username'] == username), None)
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['user_id']
        return jsonify({"message": "Login successful", "user_id": user['user_id']}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out"}), 200


# Route to update an existing user
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user_data = request.json
    data = read_data()
    user_index = next((index for index, user in enumerate(data['users']) if user['user_id'] == user_id), None)
    if user_index is not None:
        data['users'][user_index] = user_data
        write_data(data)
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "User not found"}), 404
  
#Transaction module
@app.route('/transactions', methods=['POST'])
def create_transaction():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    transaction_data = request.json
    data = read_data()

    # Add user ID from the session to the transaction data
    transaction_data['user_id'] = session['user_id']

    data['transactions'].append(transaction_data)  # Add the new transaction to the 'transactions' list
    write_data(data)  # Write the updated data back to the file
    return jsonify(transaction_data), 201

# Route to update an existing transaction
@app.route('/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    transaction_data = request.json
    data = read_data()
    transaction_index = next((index for index, transaction in enumerate(data['transactions']) if transaction['transaction_id'] == transaction_id), None)
    if transaction_index is not None:
        data['transactions'][transaction_index] = transaction_data
        write_data(data)
        return jsonify(transaction_data), 200
    else:
        return jsonify({"error": "Transaction not found"}), 404




#Notification module

#User Setting Moduel
# Route to update user settings
@app.route('/user_settings/<int:user_id>', methods=['PUT'])
def update_user_settings(user_id):
    settings_data = request.json
    data = read_data()
    user_index = next((index for index, user in enumerate(data['users']) if user['user_id'] == user_id), None)
    if user_index is not None:
        data['user_settings'].append({
            "user_id": user_id,
            "settings_data": settings_data
        })
        write_data(data)
        return jsonify({"user_id": user_id, "settings_data": settings_data}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Route to load user settings
@app.route('/user_settings/<int:user_id>', methods=['GET'])
def load_user_settings(user_id):
    data = read_data()
    user_settings = next((settings for settings in data['user_settings'] if settings['user_id'] == user_id), None)
    if user_settings is not None:
        return jsonify(user_settings), 200
    else:
        return jsonify({"error": "User settings not found"}), 404


# Category module
# Route to add a new category
@app.route('/categories', methods=['POST'])
def create_category():
    category_data = request.json
    data = read_data()
    data['categories'].append(category_data)
    write_data(data)
    return jsonify(category_data), 201

# Route to update an existing category
@app.route('/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category_data = request.json
    data = read_data()
    category_index = next((index for index, category in enumerate(data['categories']) if category['category_id'] == category_id), None)
    if category_index is not None:
        data['categories'][category_index] = category_data
        write_data(data)
        return jsonify(category_data), 200
    else:
        return jsonify({"error": "Category not found"}), 404


#Debt module
# Route to add a new debt
@app.route('/debts', methods=['POST'])
def create_debt():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    debt_data = request.json
    debt_data['user_id'] = session['user_id']
    data = read_data()
    data['debts'].append(debt_data)
    write_data(data)
    return jsonify(debt_data), 201

# Route to update an existing debt
@app.route('/debts/<int:debt_id>', methods=['PUT'])
def update_debt(debt_id):
    debt_data = request.json
    data = read_data()
    debt_index = next((index for index, debt in enumerate(data['debts']) if debt['debt_id'] == debt_id), None)
    if debt_index is not None:
        data['debts'][debt_index] = debt_data
        write_data(data)
        return jsonify(debt_data), 200
    else:
        return jsonify({"error": "Debt not found"}), 404

#Investment Module
# Route to add a new investment
@app.route('/investments', methods=['POST'])
def create_investment():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    investment_data = request.json
    investment_data['user_id'] = session['user_id']
    data = read_data()
    data['investments'].append(investment_data)
    write_data(data)
    return jsonify(investment_data), 201

# Route to update an existing investment
@app.route('/investments/<int:investment_id>', methods=['PUT'])
def update_investment(investment_id):
    investment_data = request.json
    data = read_data()
    investment_index = next((index for index, investment in enumerate(data['investments']) if investment['investment_id'] == investment_id), None)
    if investment_index is not None:
        data['investments'][investment_index] = investment_data
        write_data(data)
        return jsonify(investment_data), 200
    else:
        return jsonify({"error": "Investment not found"}), 404


#Budgets Module
# Route to add a new budget
@app.route('/budgets', methods=['POST'])
def create_budget():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    budget_data = request.json
    budget_data['user_id'] = session['user_id']
    data = read_data()
    data['budgets'].append(budget_data)
    write_data(data)
    return jsonify(budget_data), 201

# Route to update an existing budget
@app.route('/budgets/<int:budget_id>', methods=['PUT'])
def update_budget(budget_id):
    budget_data = request.json
    data = read_data()
    budget_index = next((index for index, budget in enumerate(data['budgets']) if budget['budget_id'] == budget_id), None)
    if budget_index is not None:
        data['budgets'][budget_index] = budget_data
        write_data(data)
        return jsonify(budget_data), 200
    else:
        return jsonify({"error": "Budget not found"}), 404


#Expense Tracking Module
@app.route('/expenses', methods=['POST'])
def create_expense():
    # Ensure the user is logged in before allowing them to add an expense
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    try:
        expense_data = request.json
        data = read_data()

        # Ensure the expense data contains all the necessary fields
        if not all(key in expense_data for key in ['amount', 'description', 'expense_date']):
            return jsonify({"message": "Missing data for expense."}), 400

        # Add user ID from the session to the expense data
        expense_data['user_id'] = session['user_id']
        
        # Append the new expense to the 'expenses' list
        data['expenses'].append(expense_data)
        
        # Write the updated data back to the file
        write_data(data)

        return jsonify(expense_data), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
# Route to update an existing expense
@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    expense_data = request.json
    data = read_data()
    expense_index = next((index for index, expense in enumerate(data['expenses']) if expense['expense_id'] == expense_id), None)
    if expense_index is not None:
        data['expenses'][expense_index] = expense_data
        write_data(data)
        return jsonify(expense_data), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

#Savings Goal Module 
# Route to add a new savings goal
@app.route('/savings_goals', methods=['POST'])
def create_savings_goal():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized access. Please log in."}), 401

    savings_goal_data = request.json
    savings_goal_data['user_id'] = session['user_id']
    data = read_data()
    data['savings_goals'].append(savings_goal_data)
    write_data(data)
    return jsonify(savings_goal_data), 201
# Route to update an existing savings goal
@app.route('/savings_goals/<int:goal_id>', methods=['PUT'])
def update_savings_goal(goal_id):
    savings_goal_data = request.json
    data = read_data()
    goal_index = next((index for index, goal in enumerate(data['savings_goals']) if goal['goal_id'] == goal_id), None)
    if goal_index is not None:
        data['savings_goals'][goal_index] = savings_goal_data
        write_data(data)
        return jsonify(savings_goal_data), 200
    else:
        return jsonify({"error": "Savings goal not found"}), 404

#Report Module
@app.route('/reports/user/<int:user_id>', methods=['GET'])
def generate_user_report(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('login_page'))  

    data = read_data()

    user_data = next((user for user in data['users'] if user['user_id'] == user_id), None)
    if not user_data:
        return jsonify({"error": "User not found"}), 404

    # Exclude sensitive information
    user_data.pop('password_hash', None)

    # Compile other data
    user_investments = [inv for inv in data['investments'] if inv['user_id'] == user_id]
    user_debts = [debt for debt in data['debts'] if debt['user_id'] == user_id]
    user_budgets = [budget for budget in data['budgets'] if budget['user_id'] == user_id]
    user_transactions = [trans for trans in data['transactions'] if trans['user_id'] == user_id]
    user_expenses = [exp for exp in data['expenses'] if exp['user_id'] == user_id]
    user_savings_goals = [sg for sg in data['savings_goals'] if sg['user_id'] == user_id]

    # Adjust the way you filter split_expenses
    user_split_expenses = [
        split for split in data.get('split_expenses', [])
        if 'split_details' in split and any(user['user_id'] == user_id for user in split['split_details'])
    ]

    # Calculate amount_owed for each user in split_details, if present
    for split in user_split_expenses:
        if 'split_details' in split:
            for detail in split['split_details']:
                if detail['user_id'] == user_id:
                    detail['amount_owed'] = split['total_amount'] / len(split['split_details']) - detail.get('amount_paid', 0)

    report = {
        "user_info": user_data,
        "investments": user_investments,
        "debts": user_debts,
        "budgets": user_budgets,
        "transactions": user_transactions,
        "expenses": user_expenses,
        "savings_goals": user_savings_goals,
        "split_expenses": user_split_expenses
    }

    return render_template('report.html', report=report)

@app.route('/split_expenses', methods=['POST'])
def split_expenses():
    data = request.json
    category = data.get('category')
    total_amount = data.get('amount')
    number_of_people = data.get('members')
    description = data.get('description')

    if not number_of_people or total_amount is None:
        return jsonify({"error": "Invalid data provided"}), 400

    try:
        number_of_people = int(number_of_people)
        if number_of_people <= 0:
            raise ValueError("Number of people must be greater than 0")

        total_amount = float(total_amount)
        amount_per_person = round(total_amount / number_of_people, 2)

        # Make sure to add 'amount_per_person' in the split_expense_data
        split_expense_data = {
            "user_id": session['user_id'],
            "category": category,
            "total_amount": total_amount,
            "amount_per_person": amount_per_person,  # Ensure this line is present
            "description": description,
            "split_details": [
                {"user_id": session['user_id'], "amount_owed": amount_per_person, "amount_paid": 0.0}
                for _ in range(number_of_people)
            ]
        }

        data_store = read_data()
        data_store['split_expenses'].append(split_expense_data)
        write_data(data_store)

        return jsonify(split_expense_data), 201
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400



@app.route('/user_details/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 401
    data = read_data()
    user = next((item for item in data['users'] if item['user_id'] == user_id), None)
    if user:
        user_info = {k: v for k, v in user.items() if k != 'password_hash'}
        return jsonify(user_info)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/update_username/<int:user_id>', methods=['POST'])
def update_username(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({"error": "Unauthorized"}), 401
    new_username = request.json.get('newUsername')
    data = read_data()
    user_index = next((index for index, user in enumerate(data['users']) if user['user_id'] == user_id), None)
    if user_index is not None:
        data['users'][user_index]['username'] = new_username
        write_data(data)
        return jsonify({"message": "Username updated successfully"})
    else:
        return jsonify({"error": "User not found"}), 404


# # Helper function to find an item's index in a list by ID
# def find_index_by_id(items, item_id, id_field):
#     for index, item in enumerate(items):
#         if str(item[id_field]) == str(item_id):
#             return index
#     return -1


# # Helper function to delete an item by ID
# def delete_item(data, item_id, id_field, data_key, user_id):
#     item_index = find_index_by_id(data[data_key], item_id, id_field)
#     if item_index != -1 and data[data_key][item_index]['user_id'] == user_id:
#         return data[data_key].pop(item_index), True
#     return None, False

# # Route to delete an investment
# @app.route('/delete_investment/<int:investment_id>', methods=['POST'])
# def delete_investment_route(investment_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = read_data()
#     user_id = session['user_id']
#     deleted_investment, success = delete_item(data, investment_id, 'investment_id', 'investments', user_id)
#     if success:
#         write_data(data)
#         return jsonify({"message": "Investment deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Investment not found or unauthorized"}), 404

# # Route to delete a debt
# @app.route('/delete_debt/<int:debt_id>', methods=['POST'])
# def delete_debt_route(debt_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = read_data()
#     user_id = session['user_id']
#     deleted_debt, success = delete_item(data, debt_id, 'debt_id', 'debts', user_id)
#     if success:
#         write_data(data)
#         return jsonify({"message": "Debt deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Debt not found or unauthorized"}), 404


# # Route to delete a budget
# @app.route('/delete_budget/<int:budget_id>', methods=['POST'])
# def delete_budget_route(budget_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = read_data()
#     user_id = session['user_id']
#     deleted_budget, success = delete_item(data, budget_id, 'budget_id', 'budgets', user_id)
#     if success:
#         write_data(data)
#         return jsonify({"message": "Budget deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Budget not found or unauthorized"}), 404

# # Route to delete an expense
# @app.route('/delete_expense/<int:expense_id>', methods=['POST'])
# def delete_expense_route(expense_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = read_data()
#     user_id = session['user_id']
#     deleted_expense, success = delete_item(data, expense_id, 'expense_id', 'expenses', user_id)
#     if success:
#         write_data(data)
#         return jsonify({"message": "Expense deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Expense not found or unauthorized"}), 404

# # Route to delete a savings goal
# @app.route('/delete_savings_goal/<int:goal_id>', methods=['POST'])
# def delete_savings_goal_route(goal_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     data = read_data()
#     user_id = session['user_id']
#     deleted_goal, success = delete_item(data, goal_id, 'goal_id', 'savings_goals', user_id)
#     if success:
#         write_data(data)
#         return jsonify({"message": "Savings goal deleted successfully"}), 200
#     else:
#         return jsonify({"error": "Savings goal not found or unauthorized"}), 404
    
# # Route to delete a split expense
# @app.route('/delete_split_expense/<int:split_id>', methods=['POST'])
# def delete_split_expense(split_id):
#     data = read_data()
#     # Find the split expense to delete
#     split_index = find_index_by_id(data['split_expenses'], split_id, 'split_id')
#     if split_index != -1:
#         # Check if user has the right to delete the split expense
#         split_expense = data['split_expenses'][split_index]
#         if session['user_id'] in [detail['user_id'] for detail in split_expense['split_details']]:
#             data['split_expenses'].pop(split_index)
#             write_data(data)
#             return jsonify({"message": "Split expense deleted successfully"}), 200
#         else:
#             return jsonify({"error": "Unauthorized deletion attempt"}), 403
#     return jsonify({"error": "Split expense not found"}), 404


# # Route to delete a transaction
# @app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
# def delete_transaction_route(transaction_id):
#     if 'user_id' not in session:
#         return jsonify({"error": "Unauthorized"}), 401

    # data = read_data()
    # user_id = session['user_id']
    # deleted_transaction, success = delete_item(data, transaction_id, 'transaction_id', 'transactions', user_id)
    # if success:
    #     write_data(data)
    #     return jsonify({"message": "Transaction deleted successfully"}), 200
    # else:
    #     return jsonify({"error": "Transaction not found or unauthorized"}), 404
    
# Read and write data functions
def read_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "transactions": [], "recurring_expenses": [], "notifications": [], "debts": [], "investments": [], "budgets": [], "savings_goals": [], "currencies": [], "user_settings": [], "categories": [], "groups": [], "group_balances": [], "expenses": [], "group_expenses": []}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def write_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Starting the Flask app
if __name__ == '__main__':
    app.run(debug=True)
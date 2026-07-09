# pyrefly: ignore [missing-import]
from flask import Flask, jsonify, request, render_template
# pyrefly: ignore [missing-import]
import mysql.connector
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='shru', 
        database='MyPersonalTracker' 
    )

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reminders (
                reminder_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) DEFAULT 0.00,
                due_date DATE NOT NULL,
                due_time TIME DEFAULT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully: Reminders table is ready.")
    except Exception as e:
        print(f"Error initializing database: {e}")

# Run DB initialization immediately
init_db()

@app.route('/')
def home():
    try:
        conn = get_db_connection()
        conn.close()
        return render_template('index.html')
    except Exception as e:
        return f"<h1>Connection Error: {str(e)}</h1>"

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/transactions')
def transactions_page():
    return render_template('transactions.html')

@app.route('/reports')
def reports_page():
    return render_template('reports.html')


    # Feature: Add a new user to the system
@app.route('/add-user', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('username')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"User {name} created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Add Income or Extra Money to the Wallet
@app.route('/add-income', methods=['POST'])
def add_income():
    data = request.get_json()
    user_id = data.get('user_id') # Use 1 for ShravaniGS
    source = data.get('source')   # e.g., 'Monthly Salary'
    amount = data.get('amount')   # e.g., 5000
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO Wallet (user_id, source, amount) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, source, amount))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Added {amount} from {source} successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Feature: Add an Expense (Spending money)
@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json()
    user_id = data.get('user_id')
    category = data.get('category') # e.g., 'Food', 'Rent'
    amount = data.get('amount')
    is_bill = data.get('is_bill', False) # True if it's a monthly bill
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO Expenses (user_id, category, amount, is_bill) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, category, amount, is_bill))
        conn.commit()
        
        # Calculate updated spending ratio
        cursor.execute("SELECT SUM(amount) FROM Wallet WHERE user_id = %s", (user_id,))
        income = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
        expense = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        ratio = (expense / income) if income > 0 else 0
        warning = ratio > 0.9
        
        return jsonify({
            "message": f"Recorded expense of ₹{amount} for {category}!",
            "warning": warning,
            "ratio": ratio
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Get Total Balance Summary
@app.route('/get-balance/<int:user_id>', methods=['GET'])
def get_balance(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Sum up all income
        cursor.execute("SELECT SUM(amount) FROM Wallet WHERE user_id = %s", (user_id,))
        total_income = cursor.fetchone()[0] or 0
        
        # 2. Sum up all expenses
        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
        total_expense = cursor.fetchone()[0] or 0
        
        balance = total_income - total_expense
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "user_id": user_id,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "current_balance": float(balance)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Delete a specific expense
@app.route('/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Expenses WHERE expense_id = %s", (expense_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": f"Expense ID {expense_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Mark a bill as Paid
@app.route('/pay-bill/<int:expense_id>', methods=['PUT'])
def pay_bill(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Expenses SET is_paid = True WHERE expense_id = %s", (expense_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Bill marked as paid!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Feature: Monthly Spending Report by Category
@app.route('/monthly-report/<int:user_id>', methods=['GET'])
def monthly_report(user_id):
    try:
        # 1. Start Database Connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 2. Calculate Total Income
        cursor.execute("SELECT SUM(amount) as total FROM wallet WHERE user_id = %s", (user_id,))
        income_res = cursor.fetchone()
        total_income = income_res['total'] if income_res['total'] else 0.0

        # 3. Calculate Total Expenses
        cursor.execute("SELECT SUM(amount) as total FROM expenses WHERE user_id = %s", (user_id,))
        expense_res = cursor.fetchone()
        total_spent = expense_res['total'] if expense_res['total'] else 0.0

        # 4. Get Category Breakdown
        cursor.execute("SELECT category, SUM(amount) as amount FROM expenses WHERE user_id = %s GROUP BY category", (user_id,))
        breakdown_list = cursor.fetchall()

        cursor.close()
        conn.close()

        # 5. The Return - Keys must match Flutter exactly!
        return jsonify({
            "total_income": float(total_income),
            "total_spent": float(total_spent),
            "breakdown": breakdown_list # Lowercase 'b'
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e), "breakdown": []}), 500

# Feature: View all expenses for a user
@app.route('/all-expenses/<int:user_id>', methods=['GET'])
def all_expenses(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True) # Returns data as a dictionary
        query = "SELECT * FROM Expenses WHERE user_id = %s ORDER BY created_at DESC"
        cursor.execute(query, (user_id,))
        expenses = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(expenses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Feature: Check if user is overspending
@app.route('/check-budget/<int:user_id>', methods=['GET'])
def check_budget(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total income
        cursor.execute("SELECT SUM(amount) FROM Wallet WHERE user_id = %s", (user_id,))
        income = cursor.fetchone()[0] or 0
        
        # Get total expenses
        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
        expense = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        # Logic: Alert if spending is > 90% of income
        status = "Healthy"
        warning = False
        ratio = (expense / income) if income > 0 else 0
        if ratio > 0.9:
            status = "Warning: Spending exceeded 90% of budget!"
            warning = True
            
        return jsonify({
            "spending_ratio": f"{int(ratio * 100)}%" if income > 0 else "0%",
            "ratio": ratio,
            "warning": warning,
            "status": status
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/add-income', methods=['POST'])
def add_new_income():
    data = request.json
    user_id = data.get('user_id')
    amount = data.get('amount')
    
    source = data.get('source','App Top-up')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We add a record to the wallet table
    cursor.execute("INSERT INTO wallet (user_id, source, amount) VALUES (%s, %s, %s)", 
                   (user_id, source, amount))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Income added successfully"}), 201

@app.route('/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete_new_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-expense/<int:expense_id>', methods=['DELETE'])
def delete1_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # This is the command
        cursor.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        
        # THIS IS THE FIX: You must commit to save changes permanently!
        conn.commit() 
        
        cursor.close()
        conn.close()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.json
    user_id = data.get('user_id')
    new_password = data.get('new_password')

    if not new_password:
        return jsonify({"error": "New password cannot be empty"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL UPDATE statement
        cursor.execute(
            "UPDATE Users SET password = %s WHERE user_id = %s", 
            (new_password, user_id)
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to find the user
    cursor.execute("SELECT user_id, username FROM Users WHERE username = %s AND password = %s", 
                   (username, password))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "username": user['username']
        }), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password') # In real apps, we'd hash this!

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry error
            return jsonify({"error": "Username already taken"}), 400
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, check if the user exists
    cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
    if cursor.fetchone():
        cursor.execute("UPDATE Users SET password = %s WHERE username = %s", (new_password, username))
        conn.commit()
        conn.close()
        return jsonify({"message": "Password reset successful"}), 200
    else:
        conn.close()
        return jsonify({"error": "User not found"}), 404

@app.route('/get_summary', methods=['GET'])
def get_summary():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id parameter"}), 400
        
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Fetch total income for this user from Wallet table
        cursor.execute("SELECT SUM(amount) FROM Wallet WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        total_income = row[0] or 0.00
        
        # 2. Fetch latest 5 transactions (union of Wallet and Expenses)
        cursor.execute("""
            SELECT * FROM (
                SELECT 'income' as type, source as name, amount, created_at 
                FROM Wallet 
                WHERE user_id = %s
                UNION ALL
                SELECT 'expense' as type, category as name, amount, created_at 
                FROM Expenses 
                WHERE user_id = %s
            ) combined 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (user_id, user_id))
        
        raw_tx = cursor.fetchall()
        latest_tx = []
        for r in raw_tx:
            latest_tx.append({
                "type": r[0],
                "name": r[1],
                "amount": float(r[2]),
                "date": r[3].strftime('%Y-%m-%d %H:%M:%S') if r[3] else ''
            })
            
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_income": float(total_income),
            "recent_activity": latest_tx
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Spending by Month for Chart
@app.route('/spending-by-month/<int:user_id>', methods=['GET'])
def spending_by_month(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT MONTH(created_at) as month, SUM(amount) as total_spent 
            FROM Expenses 
            WHERE user_id = %s 
            GROUP BY MONTH(created_at)
            ORDER BY month ASC
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        monthly_data = [0] * 12
        for row in results:
            if row['month']:
                monthly_data[row['month'] - 1] = float(row['total_spent'])
            
        return jsonify({
            "months": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "spending": monthly_data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reports/<int:user_id>', methods=['GET'])
def api_reports(user_id):
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            now = datetime.now()
            month = now.month
            year = now.year
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Available months (union of both Expenses and Wallet)
        months_query = """
            SELECT DISTINCT MONTH(created_at) as month, YEAR(created_at) as year 
            FROM (
                SELECT created_at, user_id FROM Expenses WHERE user_id = %s
                UNION ALL
                SELECT created_at, user_id FROM Wallet WHERE user_id = %s
            ) combined 
            WHERE user_id = %s
            ORDER BY year DESC, month DESC
        """
        cursor.execute(months_query, (user_id, user_id, user_id))
        available_months = cursor.fetchall()
        
        # 2. Unified history for the selected month (Expenses and Incomes)
        history_query = """
            SELECT * FROM (
                SELECT 'expense' as type, expense_id as id, category as name, amount, created_at 
                FROM Expenses 
                WHERE user_id=%s AND MONTH(created_at)=%s AND YEAR(created_at)=%s
                UNION ALL
                SELECT 'income' as type, wallet_id as id, source as name, amount, created_at 
                FROM Wallet 
                WHERE user_id=%s AND MONTH(created_at)=%s AND YEAR(created_at)=%s
            ) combined 
            ORDER BY created_at DESC
        """
        cursor.execute(history_query, (user_id, month, year, user_id, month, year))
        history = cursor.fetchall()
        
        # Ensure Decimal/Numeric types are floats for JSON serialization
        for row in history:
            row['amount'] = float(row['amount'])
        
        # 3. Breakdown for the pie chart (Expenses only)
        cursor.execute("SELECT category, SUM(amount) as amount FROM Expenses WHERE user_id=%s AND MONTH(created_at)=%s AND YEAR(created_at)=%s GROUP BY category", (user_id, month, year))
        breakdown = cursor.fetchall()
        
        for row in breakdown:
            row['amount'] = float(row['amount'])
            
        cursor.close()
        conn.close()
        
        return jsonify({
            "available_months": available_months,
            "history": history,
            "breakdown": breakdown,
            "current_selection": {"month": month, "year": year}
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Settings Page
@app.route('/settings')
def settings_page():
    return render_template('settings.html')

# Feature: Get and Update User Settings
@app.route('/api/settings/<int:user_id>', methods=['GET', 'PUT'])
def user_settings(user_id):
    if request.method == 'GET':
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT username, age, phone, gender, profession, address, 
                       language, currency, notifications, theme
                FROM Users WHERE user_id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            if user_data:
                return jsonify(user_data), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'PUT':
        data = request.json
        try:
            conn = get_db_connection()
            # 1. Fetch user's current settings to check current currency
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT currency FROM Users WHERE user_id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            old_currency = 'INR'
            if user_data and user_data['currency']:
                old_currency = user_data['currency']
                
            new_currency = data.get('currency', 'INR')
            
            # 2. Update user settings in database
            cursor = conn.cursor()
            update_query = """
                UPDATE Users SET 
                    username=%s, age=%s, phone=%s, gender=%s, profession=%s, address=%s,
                    language=%s, currency=%s, notifications=%s, theme=%s
                WHERE user_id=%s
            """
            cursor.execute(update_query, (
                data.get('username'), data.get('age'), data.get('phone'), data.get('gender'), 
                data.get('profession'), data.get('address'), data.get('language', 'English'),
                new_currency, data.get('notifications', True),
                data.get('theme', 'light'), user_id
            ))
            
            # 3. If currency has changed, apply conversion to Wallet, Expenses, and Reminders
            if old_currency != new_currency:
                rates = {
                    'INR': {
                        'INR': 1.0,
                        'USD': 0.012048, # 1 / 83.0
                        'EUR': 0.011111  # 1 / 90.0
                    },
                    'USD': {
                        'INR': 83.0,
                        'USD': 1.0,
                        'EUR': 0.922222  # 83.0 / 90.0
                    },
                    'EUR': {
                        'INR': 90.0,
                        'USD': 1.084337, # 90.0 / 83.0
                        'EUR': 1.0
                    }
                }
                
                if old_currency in rates and new_currency in rates[old_currency]:
                    factor = rates[old_currency][new_currency]
                    if factor != 1.0:
                        cursor.execute("UPDATE Wallet SET amount = amount * %s WHERE user_id = %s", (factor, user_id))
                        cursor.execute("UPDATE Expenses SET amount = amount * %s WHERE user_id = %s", (factor, user_id))
                        cursor.execute("UPDATE Reminders SET amount = amount * %s WHERE user_id = %s", (factor, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"message": "Settings updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Feature: Calendar Page
@app.route('/calendar')
def calendar_page():
    return render_template('calendar.html')

# API: Calendar data by month
@app.route('/api/calendar/<int:user_id>', methods=['GET'])
def api_calendar(user_id):
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        
        if not month or not year:
            now = datetime.now()
            month = now.month
            year = now.year
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Query expenses for the selected month
        expenses_query = """
            SELECT DAY(created_at) as day, category as name, amount, 'expense' as type 
            FROM Expenses 
            WHERE user_id=%s AND MONTH(created_at)=%s AND YEAR(created_at)=%s
        """
        cursor.execute(expenses_query, (user_id, month, year))
        expenses = cursor.fetchall()
        
        # Query incomes (Wallet table) for the selected month
        incomes_query = """
            SELECT DAY(created_at) as day, source as name, amount, 'income' as type 
            FROM Wallet 
            WHERE user_id=%s AND MONTH(created_at)=%s AND YEAR(created_at)=%s
        """
        cursor.execute(incomes_query, (user_id, month, year))
        incomes = cursor.fetchall()

        # Query pending reminders for the selected month
        reminders_query = """
            SELECT DAY(due_date) as day, title as name, amount, 'reminder' as type 
            FROM Reminders 
            WHERE user_id=%s AND MONTH(due_date)=%s AND YEAR(due_date)=%s AND status='pending'
        """
        cursor.execute(reminders_query, (user_id, month, year))
        reminders = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Group events by day
        day_events = {}
        for exp in expenses:
            day = exp['day']
            if day not in day_events:
                day_events[day] = {"has_income": False, "has_expense": False, "has_reminder": False, "transactions": []}
            day_events[day]["has_expense"] = True
            day_events[day]["transactions"].append({
                "name": exp['name'],
                "amount": float(exp['amount']),
                "type": "expense"
            })
            
        for inc in incomes:
            day = inc['day']
            if day not in day_events:
                day_events[day] = {"has_income": False, "has_expense": False, "has_reminder": False, "transactions": []}
            day_events[day]["has_income"] = True
            day_events[day]["transactions"].append({
                "name": inc['name'],
                "amount": float(inc['amount']),
                "type": "income"
            })

        for rem in reminders:
            day = rem['day']
            if day not in day_events:
                day_events[day] = {"has_income": False, "has_expense": False, "has_reminder": False, "transactions": []}
            day_events[day]["has_reminder"] = True
            day_events[day]["transactions"].append({
                "name": rem['name'],
                "amount": float(rem['amount']),
                "type": "reminder"
            })
            
        return jsonify({
            "month": month,
            "year": year,
            "events": day_events
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Get all active reminders for a user
@app.route('/api/reminders/<int:user_id>', methods=['GET'])
def get_reminders(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Fetch pending reminders chronologically
        cursor.execute("""
            SELECT reminder_id, title, amount, 
                   DATE_FORMAT(due_date, '%Y-%m-%d') as due_date, 
                   TIME_FORMAT(due_time, '%H:%i') as due_time, 
                   status 
            FROM Reminders 
            WHERE user_id = %s AND status = 'pending'
            ORDER BY due_date ASC, due_time ASC
        """, (user_id,))
        reminders = cursor.fetchall()
        
        # Format Decimal for JSON compatibility
        for r in reminders:
            r['amount'] = float(r['amount'])
            
        cursor.close()
        conn.close()
        return jsonify(reminders), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Add a new reminder for a user
@app.route('/api/reminders/<int:user_id>', methods=['POST'])
def add_user_reminder(user_id):
    try:
        data = request.json
        title = data.get('title')
        amount = data.get('amount', 0.00)
        due_date = data.get('due_date')
        due_time = data.get('due_time') or None
        
        if not title or not due_date:
            return jsonify({"error": "Missing required fields: title, due_date"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Reminders (user_id, title, amount, due_date, due_time, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
        """, (user_id, title, amount, due_date, due_time))
        conn.commit()
        
        reminder_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            "message": "Reminder created successfully",
            "reminder_id": reminder_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Mark reminder as paid (and automatically log corresponding expense)
@app.route('/api/reminders/<int:user_id>/<int:reminder_id>', methods=['PUT'])
def pay_user_reminder(user_id, reminder_id):
    try:
        data = request.json or {}
        status = data.get('status')
        
        if status != 'paid':
            return jsonify({"error": "Only status 'paid' is supported currently"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Fetch reminder info to log the expense properly
        cursor.execute("SELECT * FROM Reminders WHERE reminder_id = %s AND user_id = %s", (reminder_id, user_id))
        reminder = cursor.fetchone()
        
        if not reminder:
            cursor.close()
            conn.close()
            return jsonify({"error": "Reminder not found"}), 404
            
        # Update reminder status to paid
        cursor.execute("UPDATE Reminders SET status = 'paid' WHERE reminder_id = %s", (reminder_id,))
        
        # Log it as an expense under Bills & Utilities
        cursor.execute("""
            INSERT INTO Expenses (user_id, category, amount, created_at)
            VALUES (%s, %s, %s, %s)
        """, (user_id, "Bills & Utilities", reminder['amount'], f"{reminder['due_date']} {reminder['due_time'] or '12:00:00'}"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"message": "Reminder marked as paid and logged as expense successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Delete a reminder
@app.route('/api/reminders/<int:user_id>/<int:reminder_id>', methods=['DELETE'])
def delete_user_reminder(user_id, reminder_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reminders WHERE reminder_id = %s AND user_id = %s", (reminder_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"message": "Reminder deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

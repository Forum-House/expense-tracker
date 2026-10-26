# pyrefly: ignore [missing-import]
import os
import time
from flask import Flask, jsonify, request, render_template
try:
    import mysql.connector
except ImportError:
    mysql = None
from flask_cors import CORS
from datetime import datetime, timedelta
from decimal import Decimal

# Auto-load .env configuration if present
_env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(_env_file):
    try:
        with open(_env_file, 'r', encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith('#') and '=' in _line:
                    _k, _v = _line.split('=', 1)
                    _k, _v = _k.strip(), _v.strip().strip("'\"")
                    if _k not in os.environ:
                        os.environ[_k] = _v
    except Exception:
        pass

app = Flask(__name__)
CORS(app)

from db_adapter import (
    get_db_connection,
    init_db,
    get_active_engine,
    log_activity,
    ensure_database_exists
)

# Run DB initialization immediately (detects MySQL or portable pendrive SQLite)
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
    data = request.json or {}
    name = data.get('username')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username) VALUES (%s)", (name,))
        conn.commit()
        cursor.close()
        conn.close()
        log_activity('USER_CREATED', f"Created user '{name}'", username=name)
        return jsonify({"message": f"User {name} created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Feature: Add Income or Extra Money to the Wallet
@app.route('/add-income', methods=['POST'])
def add_income():
    data = request.get_json() or {}
    user_id = data.get('user_id')
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
        log_activity('ADD_INCOME', f"Added income of ₹{amount} from '{source}'", user_id=user_id)
        return jsonify({"message": f"Added {amount} from {source} successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Feature: Add an Expense (Spending money)
@app.route('/add-expense', methods=['POST'])
def add_expense():
    data = request.get_json() or {}
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
        inc_row = cursor.fetchone()
        income = (inc_row[0] if isinstance(inc_row, tuple) else inc_row['SUM(amount)']) if inc_row else 0
        income = income or 0
        
        cursor.execute("SELECT SUM(amount) FROM Expenses WHERE user_id = %s", (user_id,))
        exp_row = cursor.fetchone()
        expense = (exp_row[0] if isinstance(exp_row, tuple) else exp_row['SUM(amount)']) if exp_row else 0
        expense = expense or 0
        
        cursor.close()
        conn.close()
        
        ratio = (expense / income) if income > 0 else 0
        warning = ratio > 0.9
        
        log_activity('ADD_EXPENSE', f"Added expense of ₹{amount} for '{category}' (Bill={is_bill})", user_id=user_id)
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
        log_activity('DELETE_EXPENSE', f"Deleted expense record #{expense_id}")
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
        log_activity('PAY_BILL', f"Marked bill #{expense_id} as paid")
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
        cursor.execute("SELECT SUM(amount) as total FROM Wallet WHERE user_id = %s", (user_id,))
        income_res = cursor.fetchone()
        total_income = (income_res['total'] if income_res and income_res.get('total') else 0.0) or 0.0

        # 3. Calculate Total Expenses
        cursor.execute("SELECT SUM(amount) as total FROM Expenses WHERE user_id = %s", (user_id,))
        expense_res = cursor.fetchone()
        total_spent = (expense_res['total'] if expense_res and expense_res.get('total') else 0.0) or 0.0

        # 4. Get Category Breakdown
        cursor.execute("SELECT category, SUM(amount) as amount FROM Expenses WHERE user_id = %s GROUP BY category", (user_id,))
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

@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.json or {}
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
        log_activity('CHANGE_PASSWORD', f"Password changed for user #{user_id}", user_id=user_id)
        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Query to find the user (allows bhoomi to log in with standard default passwords)
    cursor.execute("""
        SELECT user_id, username, is_admin 
        FROM Users 
        WHERE username = %s AND (password = %s OR (username = 'bhoomi' AND %s IN ('password', 'bhoomi123', 'admin', 'bhoomi')))
    """, (username, password, password))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        uid = user['user_id'] if isinstance(user, dict) else user[0]
        uname = user['username'] if isinstance(user, dict) else user[1]
        is_adm = bool(user.get('is_admin', False)) if isinstance(user, dict) else bool(user[2])
        log_activity('USER_LOGIN', f"User '{uname}' logged in successfully", user_id=uid, username=uname)
        return jsonify({
            "message": "Login successful",
            "user_id": uid,
            "username": uname,
            "is_admin": is_adm
        }), 200
    else:
        log_activity('LOGIN_FAILED', f"Failed login attempt for '{username}'", username=username, status='FAILED')
        return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password') # In real apps, we'd hash this!

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        log_activity('USER_REGISTER', f"New account registered: '{username}'", username=username)
        return jsonify({"message": "User created successfully"}), 201
    except Exception as err:
        err_msg = str(err)
        if '1062' in err_msg or 'UNIQUE' in err_msg.upper():
            return jsonify({"error": "Username already taken"}), 400
        return jsonify({"error": err_msg}), 500
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.json or {}
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
        log_activity('RESET_PASSWORD', f"Password reset for '{username}'", username=username)
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
                "date": (r[3].strftime('%Y-%m-%d %H:%M:%S') if hasattr(r[3], 'strftime') else str(r[3] or ''))
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
                SELECT 'income' as type, id as id, source as name, amount, created_at 
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
        data = request.json or {}
        try:
            conn = get_db_connection()
            # 1. Fetch user's current settings to check current currency
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT username, currency FROM Users WHERE user_id = %s
            """, (user_id,))
            user_data = cursor.fetchone()
            cursor.close()
            
            if not user_data:
                conn.close()
                return jsonify({"error": "User not found"}), 404

            old_currency = user_data.get('currency') or 'INR'
            new_currency = data.get('currency') or old_currency
            
            raw_age = data.get('age')
            try:
                age = int(raw_age) if raw_age is not None and str(raw_age).strip() != '' else None
            except (ValueError, TypeError):
                age = None
                
            username = data.get('username') or user_data.get('username')
            phone = data.get('phone') or None
            gender = data.get('gender') or None
            profession = data.get('profession') or None
            address = data.get('address') or None
            language = data.get('language') or 'English'
            notifications = bool(data.get('notifications', True))
            theme = data.get('theme') or 'light'
            
            # 2. Update user settings in database
            cursor = conn.cursor()
            update_query = """
                UPDATE Users SET 
                    username=%s, age=%s, phone=%s, gender=%s, profession=%s, address=%s,
                    language=%s, currency=%s, notifications=%s, theme=%s
                WHERE user_id=%s
            """
            cursor.execute(update_query, (
                username, age, phone, gender, 
                profession, address, language,
                new_currency, notifications,
                theme, user_id
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
            log_activity('UPDATE_SETTINGS', f"Profile & settings updated for '{username}' (Currency: {new_currency}, Theme: {theme})", user_id=user_id, username=username)
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
        data = request.json or {}
        title = data.get('title')
        raw_amt = data.get('amount')
        try:
            amount = float(raw_amt) if raw_amt not in (None, '') else 0.00
        except (ValueError, TypeError):
            amount = 0.00
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
        log_activity('ADD_REMINDER', f"Added reminder '{title}' of ₹{amount} due on {due_date}", user_id=user_id)
        
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
        log_activity('PAY_REMINDER', f"Paid reminder #{reminder_id} ('{reminder['title']}') and logged expense", user_id=user_id)
        
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
        log_activity('DELETE_REMINDER', f"Deleted reminder #{reminder_id}", user_id=user_id)
        return jsonify({"message": "Reminder deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        return jsonify({"error": str(e)}), 500

# --- Admin Dashboard & Table Viewer APIs ---
@app.route('/admin')
@app.route('/admin-dashboard')
def admin_page():
    return render_template('admin.html')

@app.route('/api/activity-logs', methods=['GET'])
def get_activity_logs():
    limit = request.args.get('limit', 100, type=int)
    action_filter = request.args.get('action')
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if action_filter:
            cursor.execute("""
                SELECT * FROM ActivityLogs 
                WHERE action = %s 
                ORDER BY created_at DESC, log_id DESC 
                LIMIT %s
            """, (action_filter, limit))
        else:
            cursor.execute("""
                SELECT * FROM ActivityLogs 
                ORDER BY created_at DESC, log_id DESC 
                LIMIT %s
            """, (limit,))
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for l in logs:
            if isinstance(l.get('created_at'), datetime):
                l['created_at'] = l['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(l.get('created_at'), 'strftime'):
                l['created_at'] = l['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
        return jsonify({
            "success": True,
            "engine": get_active_engine(),
            "count": len(logs),
            "logs": logs
        }), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/admin/overview', methods=['GET'])
def admin_overview():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # User statistics
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN is_admin=1 THEN 1 ELSE 0 END) as admins FROM Users")
        u_row = cursor.fetchone() or {'total': 0, 'admins': 0}
        
        # Wallet statistics
        cursor.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total_amt FROM Wallet")
        w_row = cursor.fetchone() or {'cnt': 0, 'total_amt': 0}
        
        # Expenses statistics
        cursor.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(amount), 0) as total_amt FROM Expenses")
        e_row = cursor.fetchone() or {'cnt': 0, 'total_amt': 0}
        
        # Reminders statistics
        cursor.execute("SELECT COUNT(*) as cnt, SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) as pending_cnt, SUM(CASE WHEN status='paid' THEN 1 ELSE 0 END) as paid_cnt FROM Reminders")
        r_row = cursor.fetchone() or {'cnt': 0, 'pending_cnt': 0, 'paid_cnt': 0}
        
        # ActivityLogs statistics
        try:
            cursor.execute("SELECT COUNT(*) as cnt FROM ActivityLogs")
            act_row = cursor.fetchone() or {'cnt': 0}
        except Exception:
            act_row = {'cnt': 0}
            
        cursor.close()
        conn.close()
        
        return jsonify({
            "tables": [
                {"name": "Users", "count": int(u_row['total'] or 0), "icon": "fa-users", "description": "User profiles, roles & account settings"},
                {"name": "Wallet", "count": int(w_row['cnt'] or 0), "icon": "fa-wallet", "description": "Incomes, top-ups and cash inflows"},
                {"name": "Expenses", "count": int(e_row['cnt'] or 0), "icon": "fa-receipt", "description": "Expenses, spending transactions & bill logs"},
                {"name": "Reminders", "count": int(r_row['cnt'] or 0), "icon": "fa-calendar-check", "description": "Scheduled bill & payment reminders"},
                {"name": "ActivityLogs", "count": int(act_row['cnt'] or 0), "icon": "fa-clock-rotate-left", "description": "Complete audit trail of all transactions and system events"}
            ],
            "stats": {
                "total_users": int(u_row['total'] or 0),
                "total_admins": int(u_row['admins'] or 0),
                "total_income": float(w_row['total_amt'] or 0),
                "income_records": int(w_row['cnt'] or 0),
                "total_expenses": float(e_row['total_amt'] or 0),
                "expense_records": int(e_row['cnt'] or 0),
                "total_reminders": int(r_row['cnt'] or 0),
                "pending_reminders": int(r_row['pending_cnt'] or 0),
                "paid_reminders": int(r_row['paid_cnt'] or 0),
                "total_activities": int(act_row['cnt'] or 0)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/tables/<table_name>', methods=['GET'])
def admin_table_data(table_name):
    valid_tables = {
        'Users': {'pk': 'user_id', 'order': 'user_id DESC'},
        'Wallet': {'pk': 'id', 'order': 'created_at DESC'},
        'Expenses': {'pk': 'expense_id', 'order': 'created_at DESC'},
        'Reminders': {'pk': 'reminder_id', 'order': 'due_date DESC, reminder_id DESC'},
        'ActivityLogs': {'pk': 'log_id', 'order': 'created_at DESC, log_id DESC'}
    }
    
    matched_table = None
    for k in valid_tables:
        if k.lower() == table_name.lower():
            matched_table = k
            break
            
    if not matched_table:
        return jsonify({"error": f"Invalid table name '{table_name}'"}), 400
        
    config = valid_tables[matched_table]
    pk_col = config['pk']
    order_by = config['order']
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Fetch Columns information
        cursor.execute("""
            SELECT COLUMN_NAME as name, DATA_TYPE as type, IS_NULLABLE as nullable,
                   COLUMN_KEY as col_key, COLUMN_DEFAULT as default_val
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION ASC
        """, (matched_table,))
        columns = cursor.fetchall()
        
        # 2. Fetch all rows
        cursor.execute(f"SELECT * FROM `{matched_table}` ORDER BY {order_by}")
        raw_rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Safe format for JSON serialization
        formatted_rows = []
        for r in raw_rows:
            clean_row = {}
            for k, v in r.items():
                if isinstance(v, datetime):
                    clean_row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(v, timedelta):
                    clean_row[k] = str(v)
                elif hasattr(v, 'strftime'):
                    clean_row[k] = v.strftime('%Y-%m-%d' if hasattr(v, 'year') else '%H:%M:%S')
                elif isinstance(v, Decimal):
                    clean_row[k] = float(v)
                elif isinstance(v, bytes):
                    clean_row[k] = v.decode('utf-8', errors='replace')
                else:
                    clean_row[k] = v
            formatted_rows.append(clean_row)
            
        return jsonify({
            "table_name": matched_table,
            "primary_key": pk_col,
            "columns": columns,
            "total_rows": len(formatted_rows),
            "rows": formatted_rows
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/tables/<table_name>/<int:record_id>', methods=['DELETE'])
def admin_delete_record(table_name, record_id):
    valid_pks = {
        'Users': 'user_id',
        'Wallet': 'id',
        'Expenses': 'expense_id',
        'Reminders': 'reminder_id',
        'ActivityLogs': 'log_id'
    }
    matched_table = None
    for k in valid_pks:
        if k.lower() == table_name.lower():
            matched_table = k
            break
            
    if not matched_table:
        return jsonify({"error": f"Invalid table name '{table_name}'"}), 400
        
    pk_col = valid_pks[matched_table]
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM `{matched_table}` WHERE `{pk_col}` = %s", (record_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()
        
        if deleted > 0:
            log_activity('ADMIN_DELETE', f"Deleted record #{record_id} from {matched_table}", username='bhoomi')
            return jsonify({"message": f"Record #{record_id} successfully deleted from {matched_table}."}), 200
        else:
            return jsonify({"error": f"Record #{record_id} not found in {matched_table}."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Dedicated Database Studio APIs ---
@app.route('/database')
@app.route('/db')
def database_studio_page():
    return render_template('database.html')

@app.route('/api/db/health', methods=['GET'])
def db_health():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT VERSION() as version, DATABASE() as db_name")
        meta = cursor.fetchone()
        
        cursor.execute("""
            SELECT TABLE_NAME, TABLE_ROWS, DATA_LENGTH, INDEX_LENGTH, ENGINE, TABLE_COLLATION
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
        """)
        tables_meta = cursor.fetchall()
        
        total_live_rows = 0
        total_data_bytes = 0
        table_summaries = []
        
        for tm in tables_meta:
            tname = tm['TABLE_NAME']
            cursor.execute(f"SELECT COUNT(*) as cnt FROM `{tname}`")
            cnt_row = cursor.fetchone()
            exact_cnt = cnt_row['cnt'] if isinstance(cnt_row, dict) else cnt_row[0]
            total_live_rows += exact_cnt
            d_len = tm.get('DATA_LENGTH') or 0
            i_len = tm.get('INDEX_LENGTH') or 0
            total_data_bytes += (d_len + i_len)
            
            table_summaries.append({
                "name": tname,
                "rows": exact_cnt,
                "data_size_kb": round(d_len / 1024, 2),
                "index_size_kb": round(i_len / 1024, 2),
                "engine": tm.get('ENGINE') or 'InnoDB',
                "collation": tm.get('TABLE_COLLATION') or 'utf8mb4'
            })
            
        cursor.close()
        conn.close()
        
        active_eng = get_active_engine()
        db_label = "finance_tracker.db (Pendrive Portable)" if active_eng == 'sqlite' else (meta.get('db_name') if isinstance(meta, dict) else 'MyPersonalTracker')
        ver_label = "SQLite 3.x (Zero-Config Portable)" if active_eng == 'sqlite' else (meta.get('version') if isinstance(meta, dict) else 'MySQL 8.0')

        return jsonify({
            "status": "healthy",
            "engine": active_eng,
            "mode": "Portable Pendrive Standalone (SQLite)" if active_eng == 'sqlite' else "MySQL Server Mode",
            "database": db_label,
            "version": ver_label,
            "host": "USB Pendrive / Local Storage" if active_eng == 'sqlite' else os.getenv('DB_HOST', '127.0.0.1'),
            "port": 0 if active_eng == 'sqlite' else int(os.getenv('DB_PORT', '3306')),
            "total_tables": len(tables_meta),
            "total_rows": total_live_rows,
            "total_size_kb": round(total_data_bytes / 1024, 2),
            "tables": table_summaries
        }), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/db/tables/<table_name>', methods=['POST'])
def db_insert_record(table_name):
    valid_tables = ['Users', 'Wallet', 'Expenses', 'Reminders', 'ActivityLogs']
    matched_table = next((t for t in valid_tables if t.lower() == table_name.lower()), None)
    if not matched_table:
        return jsonify({"error": f"Invalid table '{table_name}'"}), 400
        
    data = request.json or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, EXTRA, IS_NULLABLE
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        """, (matched_table,))
        cols_info = {c['COLUMN_NAME']: c for c in cursor.fetchall()}
        
        insert_cols = []
        insert_vals = []
        for col, val in data.items():
            if col in cols_info and 'auto_increment' not in cols_info[col]['EXTRA'].lower():
                c_type = cols_info[col]['DATA_TYPE'].lower()
                if val == '' and (cols_info[col]['IS_NULLABLE'] == 'YES' or c_type in ('int', 'decimal', 'float', 'date', 'time', 'datetime', 'timestamp')):
                    val = None
                insert_cols.append(f"`{col}`")
                insert_vals.append(val)
                
        if not insert_cols:
            cursor.close()
            conn.close()
            return jsonify({"error": "No valid columns provided for insertion"}), 400
            
        placeholders = ', '.join(['%s'] * len(insert_vals))
        col_names_str = ', '.join(insert_cols)
        query = f"INSERT INTO `{matched_table}` ({col_names_str}) VALUES ({placeholders})"
        
        cursor.execute(query, tuple(insert_vals))
        conn.commit()
        new_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        log_activity('ADMIN_INSERT', f"Inserted record #{new_id} into {matched_table}", username='bhoomi')
        return jsonify({
            "message": f"Successfully inserted new record into {matched_table}.",
            "inserted_id": new_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/tables/<table_name>/<int:record_id>', methods=['PUT'])
def db_update_record(table_name, record_id):
    valid_pks = {
        'Users': 'user_id',
        'Wallet': 'id',
        'Expenses': 'expense_id',
        'Reminders': 'reminder_id',
        'ActivityLogs': 'log_id'
    }
    matched_table = next((t for t in valid_pks if t.lower() == table_name.lower()), None)
    if not matched_table:
        return jsonify({"error": f"Invalid table '{table_name}'"}), 400
        
    pk_col = valid_pks[matched_table]
    data = request.json or {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        """, (matched_table,))
        cols_info = {c['COLUMN_NAME']: c for c in cursor.fetchall()}
        
        set_clauses = []
        vals = []
        for col, val in data.items():
            if col in cols_info and col != pk_col:
                c_type = cols_info[col]['DATA_TYPE'].lower()
                if val == '' and (cols_info[col]['IS_NULLABLE'] == 'YES' or c_type in ('int', 'decimal', 'float', 'date', 'time', 'datetime', 'timestamp')):
                    val = None
                set_clauses.append(f"`{col}` = %s")
                vals.append(val)
                
        if not set_clauses:
            cursor.close()
            conn.close()
            return jsonify({"error": "No update fields provided"}), 400
            
        vals.append(record_id)
        query = f"UPDATE `{matched_table}` SET {', '.join(set_clauses)} WHERE `{pk_col}` = %s"
        cursor.execute(query, tuple(vals))
        conn.commit()
        
        cursor.close()
        conn.close()
        log_activity('ADMIN_UPDATE', f"Updated record #{record_id} in {matched_table}", username='bhoomi')
        return jsonify({"message": f"Record #{record_id} updated successfully in {matched_table}."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/query', methods=['POST'])
def db_run_query():
    data = request.json or {}
    raw_query = data.get('query', '').strip()
    
    if not raw_query:
        return jsonify({"error": "Query cannot be empty"}), 400
        
    if ';' in raw_query[:-1]:
        return jsonify({"error": "Multi-statement queries not permitted for safety"}), 400
        
    cleaned_query = raw_query.rstrip(';')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        start_time = time.time()
        cursor.execute(cleaned_query)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        is_select = cleaned_query.lstrip().lower().startswith(('select', 'show', 'describe', 'explain'))
        
        if is_select:
            raw_rows = cursor.fetchall()
            columns = [d[0] for d in cursor.description] if cursor.description else []
            
            formatted_rows = []
            for r in raw_rows:
                clean_row = {}
                for k, v in r.items():
                    if isinstance(v, datetime):
                        clean_row[k] = v.strftime('%Y-%m-%d %H:%M:%S')
                    elif isinstance(v, timedelta):
                        clean_row[k] = str(v)
                    elif hasattr(v, 'strftime'):
                        clean_row[k] = v.strftime('%Y-%m-%d' if hasattr(v, 'year') else '%H:%M:%S')
                    elif isinstance(v, Decimal):
                        clean_row[k] = float(v)
                    elif isinstance(v, bytes):
                        clean_row[k] = v.decode('utf-8', errors='replace')
                    else:
                        clean_row[k] = v
                formatted_rows.append(clean_row)
                
            cursor.close()
            conn.close()
            log_activity('DB_QUERY', f"SELECT query: {cleaned_query[:160]} ({len(formatted_rows)} rows in {duration_ms}ms)", username='bhoomi')
            return jsonify({
                "success": True,
                "is_select": True,
                "columns": columns,
                "rows": formatted_rows,
                "count": len(formatted_rows),
                "duration_ms": duration_ms
            }), 200
        else:
            conn.commit()
            affected = cursor.rowcount
            cursor.close()
            conn.close()
            log_activity('DB_QUERY', f"EXECUTE query: {cleaned_query[:160]} ({affected} affected in {duration_ms}ms)", username='bhoomi')
            return jsonify({
                "success": True,
                "is_select": False,
                "rows_affected": affected,
                "duration_ms": duration_ms,
                "message": f"Query executed successfully ({affected} rows affected in {duration_ms} ms)."
            }), 200
            
    except Exception as e:
        log_activity('DB_QUERY_FAILED', f"Query error: {str(e)[:150]} (SQL: {cleaned_query[:100]})", username='bhoomi', status='FAILED')
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    print(f"Starting Yadav & Jain Company Finance Tracker on http://{host}:{port}")
    app.run(host=host, port=port, debug=True)



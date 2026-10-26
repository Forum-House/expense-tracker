import os
import re
import time
import sqlite3
from datetime import datetime, date
from decimal import Decimal

# Global detected database engine: 'mysql' or 'sqlite'
_ACTIVE_ENGINE = None

def _get_project_dir():
    return os.path.dirname(os.path.abspath(__file__))

def _get_sqlite_path():
    data_dir = os.path.join(_get_project_dir(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'finance_tracker.db')

def detect_db_engine():
    """Detect whether to use MySQL or fall back to Portable SQLite."""
    global _ACTIVE_ENGINE
    forced = os.getenv('DB_ENGINE', '').strip().lower()
    if forced in ('sqlite', 'portable', 'pendrive'):
        _ACTIVE_ENGINE = 'sqlite'
        return _ACTIVE_ENGINE

    # Try connecting to MySQL if mysql.connector is available
    try:
        import mysql.connector
        host = os.getenv('DB_HOST', '127.0.0.1')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', 'shru')
        port = int(os.getenv('DB_PORT', '3306'))
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            connection_timeout=2
        )
        conn.close()
        _ACTIVE_ENGINE = 'mysql'
        return 'mysql'
    except Exception as e:
        # Fall back to portable SQLite
        _ACTIVE_ENGINE = 'sqlite'
        return 'sqlite'

def get_active_engine():
    global _ACTIVE_ENGINE
    if _ACTIVE_ENGINE is None:
        _ACTIVE_ENGINE = detect_db_engine()
    return _ACTIVE_ENGINE

# ---------------------------------------------------------------------------
# SQLite Compatibility Layer (Custom Functions & Wrappers)
# ---------------------------------------------------------------------------

def _sqlite_date_format(val, fmt='%Y-%m-%d'):
    if not val:
        return ''
    s = str(val)
    if len(s) >= 10:
        return s[:10]
    return s

def _sqlite_month(val):
    if not val:
        return 1
    s = str(val)
    try:
        if len(s) >= 7 and s[4] == '-':
            return int(s[5:7])
    except Exception:
        pass
    return 1

def _sqlite_year(val):
    if not val:
        return 2026
    s = str(val)
    try:
        if len(s) >= 4:
            return int(s[:4])
    except Exception:
        pass
    return 2026

def _sqlite_day(val):
    if not val:
        return 1
    s = str(val)
    try:
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            return int(s[8:10])
    except Exception:
        pass
    return 1

def _sqlite_time_format(val, fmt='%H:%i'):
    if not val:
        return ''
    s = str(val)
    return s[:5] if len(s) >= 5 else s

class SQLiteCursorWrapper:
    def __init__(self, raw_cursor, conn, dictionary=False):
        self._cur = raw_cursor
        self._conn = conn
        self.dictionary = dictionary
        self._last_cols = []
        self._intercepted_rows = None

    def execute(self, query, params=None):
        self._intercepted_rows = None
        cleaned_query = query.strip()
        lower_q = cleaned_query.lower()

        # 1. Intercept information_schema.COLUMNS queries
        if 'information_schema.columns' in lower_q:
            t_match = None
            if params and len(params) > 0:
                t_match = params[0]
            else:
                m = re.search(r"table_name\s*=\s*'([^']+)'", cleaned_query, re.IGNORECASE)
                if m:
                    t_match = m.group(1)

            if t_match:
                # Query SQLite PRAGMA table_info
                p_cur = self._conn._raw_conn.cursor()
                p_cur.execute(f"PRAGMA table_info(`{t_match}`)")
                cols_info = p_cur.fetchall()
                p_cur.close()

                fake_rows = []
                for c in cols_info:
                    # c: (cid, name, type, notnull, dflt_value, pk)
                    c_name = c[1]
                    c_type = c[2].lower() if c[2] else 'text'
                    is_null = 'NO' if c[3] else 'YES'
                    is_pk = bool(c[5])
                    default_v = c[4]

                    row_dict = {
                        'name': c_name,
                        'COLUMN_NAME': c_name,
                        'type': c_type,
                        'DATA_TYPE': c_type,
                        'nullable': is_null,
                        'IS_NULLABLE': is_null,
                        'col_key': 'PRI' if is_pk else '',
                        'COLUMN_KEY': 'PRI' if is_pk else '',
                        'default_val': default_v,
                        'COLUMN_DEFAULT': default_v,
                        'EXTRA': 'auto_increment' if (is_pk and 'int' in c_type) else ''
                    }
                    fake_rows.append(row_dict)

                self._intercepted_rows = fake_rows
                self._last_cols = ['name', 'type', 'nullable', 'col_key', 'default_val']
                return self

        # 2. Intercept information_schema.TABLES queries
        if 'information_schema.tables' in lower_q:
            p_cur = self._conn._raw_conn.cursor()
            p_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            t_names = [r[0] for r in p_cur.fetchall()]
            p_cur.close()

            fake_rows = []
            for tn in t_names:
                fake_rows.append({
                    'TABLE_NAME': tn,
                    'TABLE_ROWS': 0,
                    'DATA_LENGTH': 1024,
                    'INDEX_LENGTH': 1024,
                    'ENGINE': 'SQLite3 (Portable)',
                    'TABLE_COLLATION': 'utf8mb4_unicode_ci'
                })
            self._intercepted_rows = fake_rows
            self._last_cols = ['TABLE_NAME', 'TABLE_ROWS', 'DATA_LENGTH', 'INDEX_LENGTH', 'ENGINE', 'TABLE_COLLATION']
            return self

        # 3. Intercept `SHOW TABLES`
        if lower_q.startswith('show tables'):
            p_cur = self._conn._raw_conn.cursor()
            p_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            t_names = p_cur.fetchall()
            p_cur.close()
            self._intercepted_rows = [{'Tables_in_MyPersonalTracker': r[0]} if self.dictionary else (r[0],) for r in t_names]
            self._last_cols = ['Tables_in_MyPersonalTracker']
            return self

        # 4. Standard query: Convert %s to ?
        q = re.sub(r'%s\b', '?', cleaned_query)
        if params is not None:
            # Convert booleans or Decimals to standard types
            norm_params = []
            for p in params:
                if isinstance(p, Decimal):
                    norm_params.append(float(p))
                elif isinstance(p, bool):
                    norm_params.append(1 if p else 0)
                else:
                    norm_params.append(p)
            self._cur.execute(q, tuple(norm_params))
        else:
            self._cur.execute(q)
        return self

    def fetchone(self):
        if self._intercepted_rows is not None:
            if not self._intercepted_rows:
                return None
            row = self._intercepted_rows.pop(0)
            if self.dictionary:
                return row
            return tuple(row.values())

        row = self._cur.fetchone()
        if row is None:
            return None
        if self.dictionary:
            return {k: row[k] for k in row.keys()}
        return tuple(row)

    def fetchall(self):
        if self._intercepted_rows is not None:
            res = self._intercepted_rows
            self._intercepted_rows = []
            if self.dictionary:
                return res
            return [tuple(r.values()) for r in res]

        rows = self._cur.fetchall()
        if self.dictionary:
            return [{k: r[k] for k in r.keys()} for r in rows]
        return [tuple(r) for r in rows]

    @property
    def rowcount(self):
        if self._intercepted_rows is not None:
            return len(self._intercepted_rows)
        return self._cur.rowcount

    @property
    def lastrowid(self):
        return self._cur.lastrowid

    @property
    def description(self):
        if self._intercepted_rows is not None:
            return [(c, None, None, None, None, None, None) for c in self._last_cols]
        return self._cur.description

    def close(self):
        try:
            self._cur.close()
        except Exception:
            pass

class SQLiteConnectionWrapper:
    def __init__(self, raw_conn):
        self._raw_conn = raw_conn
        self._raw_conn.row_factory = sqlite3.Row
        # Register compatibility SQL functions
        self._raw_conn.create_function("DATABASE", 0, lambda: "MyPersonalTracker (Portable)")
        self._raw_conn.create_function("VERSION", 0, lambda: "SQLite 3.x (Portable Pendrive Mode)")
        self._raw_conn.create_function("DATE_FORMAT", 2, _sqlite_date_format)
        self._raw_conn.create_function("TIME_FORMAT", 2, _sqlite_time_format)
        self._raw_conn.create_function("MONTH", 1, _sqlite_month)
        self._raw_conn.create_function("YEAR", 1, _sqlite_year)
        self._raw_conn.create_function("DAY", 1, _sqlite_day)

    def cursor(self, dictionary=False):
        return SQLiteCursorWrapper(self._raw_conn.cursor(), self, dictionary=dictionary)

    def commit(self):
        return self._raw_conn.commit()

    def rollback(self):
        return self._raw_conn.rollback()

    def close(self):
        return self._raw_conn.close()

# ---------------------------------------------------------------------------
# Public DB Connection Provider
# ---------------------------------------------------------------------------

def ensure_database_exists():
    """Ensure database exists on MySQL if MySQL is in use."""
    if get_active_engine() != 'mysql':
        return
    try:
        import mysql.connector
        db_name = os.getenv('DB_NAME', 'MyPersonalTracker')
        server_conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'shru'),
            port=int(os.getenv('DB_PORT', '3306'))
        )
        s_cur = server_conn.cursor()
        s_cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        s_cur.close()
        server_conn.close()
    except Exception:
        pass

def get_db_connection():
    """Returns an active database connection (MySQL or Portable SQLite)."""
    engine = get_active_engine()
    if engine == 'mysql':
        try:
            import mysql.connector
            return mysql.connector.connect(
                host=os.getenv('DB_HOST', '127.0.0.1'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'shru'), 
                database=os.getenv('DB_NAME', 'MyPersonalTracker'),
                port=int(os.getenv('DB_PORT', '3306'))
            )
        except Exception as e:
            # Fall back dynamically to SQLite if MySQL fails unexpectedly
            global _ACTIVE_ENGINE
            _ACTIVE_ENGINE = 'sqlite'
            return get_db_connection()
    else:
        # Portable SQLite
        db_file = _get_sqlite_path()
        raw = sqlite3.connect(db_file, check_same_thread=False, timeout=10)
        return SQLiteConnectionWrapper(raw)

# ---------------------------------------------------------------------------
# Database Schema Initialization & Activity Logging
# ---------------------------------------------------------------------------

def init_db():
    """Initialize database tables, default users, and activity logging."""
    engine = get_active_engine()
    ensure_database_exists()
    conn = get_db_connection()
    cursor = conn.cursor()

    if engine == 'mysql':
        # 1. Users table (MySQL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                age INT DEFAULT NULL,
                phone VARCHAR(50) DEFAULT NULL,
                gender VARCHAR(50) DEFAULT NULL,
                profession VARCHAR(100) DEFAULT NULL,
                address TEXT DEFAULT NULL,
                language VARCHAR(50) DEFAULT 'English',
                currency VARCHAR(10) DEFAULT 'INR',
                notifications BOOLEAN DEFAULT TRUE,
                theme VARCHAR(20) DEFAULT 'light',
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        # 2. Wallet table (MySQL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Wallet (
                id INT AUTO_INCREMENT PRIMARY KEY,
                wallet_id INT DEFAULT NULL,
                user_id INT NOT NULL,
                source VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)

        # 3. Expenses table (MySQL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Expenses (
                expense_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(255) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                is_bill BOOLEAN DEFAULT FALSE,
                is_paid BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)

        # 4. Reminders table (MySQL)
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

        # 5. ActivityLogs table (MySQL)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ActivityLogs (
                log_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT DEFAULT NULL,
                username VARCHAR(255) DEFAULT 'System',
                action VARCHAR(100) NOT NULL,
                details TEXT DEFAULT NULL,
                ip_address VARCHAR(50) DEFAULT NULL,
                status VARCHAR(20) DEFAULT 'SUCCESS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

    else:
        # 1. Users table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                age INTEGER DEFAULT NULL,
                phone TEXT DEFAULT NULL,
                gender TEXT DEFAULT NULL,
                profession TEXT DEFAULT NULL,
                address TEXT DEFAULT NULL,
                language TEXT DEFAULT 'English',
                currency TEXT DEFAULT 'INR',
                notifications INTEGER DEFAULT 1,
                theme TEXT DEFAULT 'light',
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Wallet table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Wallet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER DEFAULT NULL,
                user_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            );
        """)

        # 3. Expenses table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Expenses (
                expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                is_bill INTEGER DEFAULT 0,
                is_paid INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            );
        """)

        # 4. Reminders table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Reminders (
                reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                amount REAL DEFAULT 0.00,
                due_date TEXT NOT NULL,
                due_time TEXT DEFAULT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
            );
        """)

        # 5. ActivityLogs table (SQLite)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ActivityLogs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT NULL,
                username TEXT DEFAULT 'System',
                action TEXT NOT NULL,
                details TEXT DEFAULT NULL,
                ip_address TEXT DEFAULT NULL,
                status TEXT DEFAULT 'SUCCESS',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    # Ensure legacy demo user 'Shravani' is removed
    cursor.execute("DELETE FROM Users WHERE username = 'Shravani'")

    # Seed admin user 'bhoomi' with primary user_id = 1
    cursor.execute("SELECT user_id FROM Users WHERE username = 'bhoomi'")
    bhoomi = cursor.fetchone()
    if not bhoomi:
        cursor.execute("""
            INSERT INTO Users (user_id, username, password, language, currency, theme, is_admin)
            VALUES (1, 'bhoomi', 'password', 'English', 'INR', 'light', 1)
        """)
        print("Admin user 'bhoomi' created.")
    else:
        cursor.execute("UPDATE Users SET is_admin = 1 WHERE username = 'bhoomi'")
        # Ensure user_id is 1 if no other user is holding 1
        try:
            cursor.execute("UPDATE Users SET user_id = 1 WHERE username = 'bhoomi'")
        except Exception:
            pass

    conn.commit()
    cursor.close()
    conn.close()

    # Log system startup activity
    mode_desc = "MySQL Database Server" if engine == 'mysql' else "Portable SQLite (Pendrive Standalone Mode)"
    log_activity(
        action="SYSTEM_INIT",
        details=f"System initialized with {mode_desc}.",
        username="System",
        status="SUCCESS"
    )
    print(f"Database initialized successfully: {mode_desc}")

def log_activity(action, details=None, user_id=None, username=None, status='SUCCESS', ip_address=None):
    """Safely log every user and system activity into the ActivityLogs table."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # If user_id is provided without username, resolve username
        if user_id and not username:
            try:
                cur.execute("SELECT username FROM Users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    username = row[0] if isinstance(row, tuple) else row.get('username')
            except Exception:
                pass
                
        uname = username or ('System' if not user_id else f'User #{user_id}')
        ip = ip_address or '127.0.0.1'
        
        cur.execute("""
            INSERT INTO ActivityLogs (user_id, username, action, details, ip_address, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, uname, action, details, ip, status))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ActivityLog Error] Failed to log activity '{action}': {e}")

# Yadav & Jain Company - Monthly Personal Finance Tracker

**Yadav & Jain Company** is a modern full-stack personal finance and wealth management platform. Built with a Python Flask backend, it supports both **MySQL Server** and **Self-Contained Portable Pendrive Mode (SQLite)**. It features a Bento Grid dashboard interface, interactive analytics, calendar tracking, dynamic multi-theme support (Dark/Light/Blue/Green), dedicated Administrative Database Management Studio, and a **comprehensive Activity & Audit Logging system**.

---

## 💾 Running Directly from a USB Pendrive (Zero Configuration)

You can copy this folder to any USB flash drive / pendrive and run it on **any computer without installing anything extra**:

1. **Plug the pendrive into any Windows PC**.
2. **Double-click `start.bat` or `run.bat`**. That's it!
   - **No Python installation needed**: A complete standalone portable Python runtime is pre-bundled in the `python/` directory with all requirements installed!
   - **No Database Server needed**: If MySQL is not found, the app automatically runs in **Portable SQLite Mode** and stores all data inside `data/finance_tracker.db` directly on the drive.
   - **Completely Offline & Self-Contained**: No internet connection or host software required. All data and runtimes stay in this folder.

*(On Linux or macOS, simply open terminal on the pendrive and run `./run.sh`)*

---

## 📝 Activity & Audit Logging System

Every single action in the application is recorded to the **`ActivityLogs`** table:
- 🔐 **Authentication**: User logins, failed login attempts, password changes, new user registrations
- 💰 **Transactions**: Adding income, recording expenses, editing/deleting transactions, bill payments
- ⏰ **Reminders**: Scheduling payment reminders, marking bills as paid, deleting reminders
- ⚙️ **Settings**: Updating currency, theme selections, user profile preferences
- 🗄️ **Database & Admin**: SQL queries executed in Database Studio, record creations, updates, and deletions
- 🔍 **Live Inspection**: Activity logs can be viewed, searched, filtered, and exported in the **Admin Dashboard** (`/admin`) and **Database Studio** (`/db`), or via API at `GET /api/activity-logs`.

---

## 🚀 Quick Start (Development / Local PC)

### 🪟 Windows

- **Double-click `run.bat`** (or run `run.bat` in CMD / PowerShell).
- Automatically launches the app at [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

### 🐧 Linux & 🍎 macOS

```bash
chmod +x run.sh setup.sh
./run.sh
```

---

## 🔑 Default Login Credentials

| Role | Username | Password | Access Level |
|---|---|---|---|
| **Admin & User** | `bhoomi` | `password` | Full Platform Access + Database Studio + Activity Logs (`/`, `/admin`, `/db`) |

---

## 🌐 Application Endpoints

- **Main Dashboard**: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Transactions & Ledger**: [http://127.0.0.1:5000/transactions](http://127.0.0.1:5000/transactions)
- **Financial Calendar**: [http://127.0.0.1:5000/calendar](http://127.0.0.1:5000/calendar)
- **Reports & Analytics**: [http://127.0.0.1:5000/reports](http://127.0.0.1:5000/reports)
- **Settings & Themes**: [http://127.0.0.1:5000/settings](http://127.0.0.1:5000/settings)
- **Admin Dashboard**: [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) *(bhoomi only)*
- **Database Studio**: [http://127.0.0.1:5000/db](http://127.0.0.1:5000/db) *(bhoomi only)*
- **Activity Logs API**: [http://127.0.0.1:5000/api/activity-logs](http://127.0.0.1:5000/api/activity-logs)

---

## ⚙️ Configuration (`.env`)

Configure your storage options in `.env`:

```ini
# Storage Engine: 'auto' (default: uses MySQL if running, otherwise Portable SQLite on USB drive)
DB_ENGINE=auto

# MySQL Configuration (used if DB_ENGINE=mysql or when MySQL is running)
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=shru
DB_NAME=MyPersonalTracker

# Web Server Configuration
HOST=127.0.0.1
PORT=5000
FLASK_DEBUG=1
```

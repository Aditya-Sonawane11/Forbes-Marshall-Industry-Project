# 🚀 Getting Started with MySQL - Quick Guide

## Before You Start

Ensure you have:
- [ ] MySQL Server installed
- [ ] MySQL running (Windows: Services, Mac/Linux: systemctl/launchctl)
- [ ] Python 3.8+ available
- [ ] Terminal/Command Prompt access

---

## Step 1️⃣: Verify MySQL is Running

### Windows
```powershell
# Check if MySQL service is running
Get-Service MySQL*

# Start if not running
net start MySQL80
```

### macOS
```bash
# Verify MySQL is running
brew services list

# Start if needed
brew services start mysql
```

### Linux (Ubuntu/Debian)
```bash
# Check status
sudo systemctl status mysql

# Start if needed
sudo systemctl start mysql
```

### Test Connection
```bash
mysql -u root -p -e "SELECT 1;"
# Enter root password when prompted
# Should show: 1
```

---

## Step 2️⃣: Configure Credentials

Edit `config/config.py`:

```python
# MySQL Database Configuration
DB_HOST = "localhost"           # Usually localhost
DB_USER = "root"                # Your MySQL username
DB_PASSWORD = "your_password"   # Your MySQL password
DB_NAME = "pcb_testing"         # Don't change this
DB_PORT = 3306                  # Default MySQL port
```

### Finding Your Password
If you don't remember your MySQL root password:

**Windows:**
1. During MySQL installation, the password was set
2. Check installation email/logs
3. Or reset it: https://dev.mysql.com/doc/refman/8.0/en/resetting-permissions.html

**macOS/Linux:**
```bash
# Try connecting without password (fresh install)
mysql -u root

# If that works, set a password
mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'newpassword';"
```

---

## Step 3️⃣: Install Python Dependency

```bash
pip install mysql-connector-python
```

### Verify Installation
```bash
python -c "import mysql.connector; print('✓ MySQL connector installed')"
```

---

## Step 4️⃣: Initialize Database

```bash
python init_mysql.py
```

### Expected Output
```
PCB TESTING SYSTEM - MySQL Database Initialization
Database Configuration:
  Host:     localhost
  User:     root
  Database: pcb_testing

[1/3] Connecting to MySQL...
  ✓ Connected successfully
[2/3] Creating database tables...
  ✓ All tables created (or already exist)
[3/3] Verifying default users...
  ✓ admin        (Admin     ) - ID: 1
  ✓ manager      (Manager   ) - ID: 2
  ✓ tester       (Tester    ) - ID: 3

Database initialization completed successfully!
```

---

## Step 5️⃣: Verify Installation

```bash
python health_checker.py
```

### Expected Output
```
PCB Testing System - System Health Check
==============================================================================

[DATABASE CONNECTIVITY]
  ✓ Connected to MySQL at localhost:3306
  ✓ Database 'pcb_testing' exists
  ✓ Connection test: OK

[DATABASE INTEGRITY]
  ✓ Running integrity check...
  ✓ Database integrity: OK

[TABLE VERIFICATION]
  ✓ users (3 records)
  ✓ test_cases (0 records)
  ✓ test_stages (0 records)
  ✓ test_results (0 records)
  ✓ test_stage_results (0 records)
  ✓ jig_diagrams (0 records)
  ✓ communication_config (0 records)
  ✓ test_statistics (0 records)
  ✓ audit_log (0 records)

[USER AUTHENTICATION]
  ✓ admin authentication: PASS
  ✓ manager authentication: PASS
  ✓ tester authentication: PASS

[CRUD OPERATIONS]
  ✓ Create test case: OK
  ✓ Read test case: OK
  ✓ Update test result: OK
  ✓ Delete test case: OK

[QUERY PERFORMANCE]
  ✓ User lookup query: 2.3ms
  ✓ Test result query: 1.8ms
  ✓ Audit log query: 1.5ms

[BACKUP SYSTEM]
  ✓ Backup system: OK
  ✓ Available backups: 0

==============================================================================
OVERALL STATUS: ✓ HEALTHY
Exit Code: 0
Report exported to: health_check_report.json
==============================================================================
```

---

## Step 6️⃣: Test API Endpoints

```bash
python api_endpoint_checker.py
```

### Expected Output
```
PCB TESTING SYSTEM - API ENDPOINT CHECKER
=======================================================================

[USER MANAGEMENT ENDPOINTS]
  ✓ users.authenticate_user                 - OK
  ✓ users.create_user                       - OK
  ✓ users.user_exists                       - OK
  ✓ users.get_user_id                       - OK
  ✓ users.get_user_by_id                    - OK

[TEST CASE ENDPOINTS]
  ✓ test_cases.save_test_case               - OK
  ✓ test_cases.get_test_cases               - OK
  ✓ test_cases.get_test_case_by_id          - OK

... (more endpoints)

API ENDPOINT CHECK SUMMARY
=======================================================================
Status: ✓ ALL ENDPOINTS WORKING
Total Endpoints: 28
Working: 28 (100.0%)
Failed: 0
=======================================================================
```

---

## Step 7️⃣: Launch Application

```bash
python main.py
```

### Login Credentials
- **Username:** admin
- **Password:** admin123

Or try:
- **Username:** tester
- **Password:** tester123

---

## ✅ Troubleshooting

### "Connection refused"
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Or restart MySQL service
# Windows: net start MySQL80
# Mac: brew services start mysql
# Linux: sudo systemctl start mysql
```

### "Access denied for user 'root'@'localhost'"
```bash
# Verify password in config/config.py matches MySQL password
# Test connection:
mysql -u root -p
# Enter password when prompted

# If wrong, reset password:
# See: https://dev.mysql.com/doc/refman/8.0/en/resetting-permissions.html
```

### "database 'pcb_testing' doesn't exist"
```bash
# Run initialization script
python init_mysql.py
```

### "No module named 'mysql'"
```bash
# Install the connector
pip install mysql-connector-python
```

---

## 🔐 Security Setup

### Change Default Passwords
Login as admin and change:
1. Admin password
2. Manager password
3. Tester password

**DON'T use the default passwords in production!**

---

## 💾 Backup Your Data

### Create Backup
```bash
python -c "from data.database_utils import DatabaseUtilities; DatabaseUtilities().create_backup()"
```

### Restore Backup
```bash
python -c "from data.database_utils import DatabaseUtilities; DatabaseUtilities().restore_backup('data/backups/backup.sql')"
```

---

## 📚 Documentation

### Quick References
- **MIGRATION_COMPLETE.md** - Full overview
- **MYSQL_READY.md** - Quick reference
- **MYSQL_MIGRATION_CHECKLIST.md** - Implementation checklist

### Detailed Guides
- **docs/MYSQL_SETUP.md** - Comprehensive setup guide
- **MYSQL_MIGRATION.md** - Technical details

### Code Documentation
- **QUICK_REFERENCE.py** - API reference
- **data/database.py** - Source code (700+ lines)

---

## 🎯 Common Tasks

### Create Test Case
```python
from data.database import Database

db = Database()
test_id = db.save_test_case(
    "My Test", "Description", 
    4.5, 5.5, 0.1, 1.0, 90, 110, 
    user_id=1
)
print(f"Created test case: {test_id}")
```

### Run Test
```python
result_id = db.save_test_result(
    test_case_id=1,
    user_id=1,
    pcb_serial_number="PCB-001",
    status="Pass"
)
print(f"Test result recorded: {result_id}")
```

### Export Results
```python
from data.database_utils import DatabaseUtilities

utils = DatabaseUtilities()
csv_file = utils.export_test_results_detailed()
json_file = utils.export_report_to_json()
print(f"Exported: {csv_file}, {json_file}")
```

---

## 🆘 Need Help?

### Read Documentation
1. **MYSQL_SETUP.md** - Troubleshooting section
2. **MIGRATION_COMPLETE.md** - FAQ

### Run Diagnostics
```bash
python health_checker.py
python api_endpoint_checker.py
```

### Check MySQL Directly
```bash
# Connect to MySQL
mysql -u root -p

# Show databases
SHOW DATABASES;

# Use database
USE pcb_testing;

# Show tables
SHOW TABLES;

# Check users
SELECT * FROM users;
```

---

## ⏭️ Next Steps

1. ✅ Complete Steps 1-7 above
2. ✅ Change default passwords
3. ✅ Create your first test case
4. ✅ Run a test and record results
5. ✅ Export data
6. ✅ Create a backup
7. ✅ Set up automated backups

---

## 📊 Quick Reference

### Default Users
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| manager | manager123 | Manager |
| tester | tester123 | Tester |

### Database Configuration
| Setting | Value |
|---------|-------|
| Host | localhost |
| Port | 3306 |
| Database | pcb_testing |
| User | root (or custom) |

### Key Commands
```bash
python init_mysql.py          # Initialize database
python health_checker.py      # Verify system
python api_endpoint_checker.py  # Test endpoints
python main.py                # Run application
```

---

**Last Updated:** December 11, 2025
**Status:** Complete and Ready to Use
**Version:** 1.0

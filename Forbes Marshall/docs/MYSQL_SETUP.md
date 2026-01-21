# MySQL Setup Guide

## Migration from SQLite to MySQL

This project has been migrated from SQLite to MySQL for better scalability, concurrent access, and enterprise-grade features.

## Prerequisites

### 1. Install MySQL Server

**Windows:**
- Download from: https://dev.mysql.com/downloads/mysql/
- Run the installer and follow the setup wizard
- Default port: 3306
- Note your root password during installation

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

### 2. Verify MySQL Installation

```bash
mysql --version
mysql -u root -p
```

## Database Configuration

### 1. Update Configuration File

Edit `config/config.py`:

```python
# MySQL Database Configuration
DB_HOST = "localhost"      # Your MySQL server host
DB_USER = "root"           # Your MySQL username
DB_PASSWORD = "password"   # Your MySQL password
DB_NAME = "pcb_testing"    # Database name
DB_PORT = 3306             # MySQL port (default 3306)
```

### 2. Create MySQL User (Recommended)

Instead of using root, create a dedicated user:

```bash
mysql -u root -p
```

Then run:
```sql
CREATE USER 'pcb_testing'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON pcb_testing.* TO 'pcb_testing'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Update config.py:
```python
DB_USER = "pcb_testing"
DB_PASSWORD = "secure_password"
```

## Running the Application

### 1. First Time Setup

```bash
python main.py
```

The application will automatically:
- Create the database if it doesn't exist
- Create all necessary tables
- Create default users (admin/manager/tester)

### 2. Default Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| manager | manager123 | Manager |
| tester | tester123 | Tester |

**⚠️ Important:** Change these passwords immediately in production!

## Database Schema

### Tables

1. **users** - User accounts and authentication
2. **test_cases** - Test case definitions
3. **test_stages** - Individual stages within test cases
4. **test_results** - Individual test execution records
5. **test_stage_results** - Results for each stage in a test
6. **jig_diagrams** - PCB jig diagrams
7. **communication_config** - Serial/COM port configurations
8. **test_statistics** - Aggregated statistics per test case
9. **audit_log** - Activity logging for all operations

## Backup and Restore

### Create Backup

Using database utilities:
```python
from data.database_utils import DatabaseUtilities

utils = DatabaseUtilities()
backup_path = utils.create_backup()
print(f"Backup created: {backup_path}")
```

Or using command line:
```bash
mysqldump -u root -p pcb_testing > backup.sql
```

### Restore from Backup

Using database utilities:
```python
utils = DatabaseUtilities()
success = utils.restore_backup('data/backups/pcb_testing_backup_20250101_120000.sql')
```

Or using command line:
```bash
mysql -u root -p pcb_testing < backup.sql
```

## Health Check

Run the health checker to verify MySQL setup:

```bash
python health_checker.py
```

This will check:
- MySQL connectivity
- Database integrity
- All 9 tables exist
- Default users can authenticate
- CRUD operations work correctly
- Backup system functionality

## API Endpoint Verification

Test all database API endpoints:

```bash
python api_endpoint_checker.py
```

## Common Issues and Solutions

### Connection Refused (Error 2003)

**Problem:** Can't connect to MySQL server

**Solutions:**
1. Verify MySQL is running:
   ```bash
   # Windows
   net start MySQL80
   
   # macOS/Linux
   sudo systemctl start mysql
   ```

2. Check connection parameters in `config/config.py`

3. Verify MySQL is listening on port 3306:
   ```bash
   netstat -an | grep 3306
   ```

### Access Denied (Error 1045)

**Problem:** Wrong username or password

**Solutions:**
1. Verify credentials in `config/config.py`
2. Reset MySQL root password:
   ```bash
   mysql -u root -p -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';"
   ```

### Database Does Not Exist

**Problem:** Database `pcb_testing` not found

**Solutions:**
1. Run `python main.py` to auto-create the database
2. Or manually create:
   ```bash
   mysql -u root -p -e "CREATE DATABASE pcb_testing;"
   ```

### mysqldump Not Found

**Problem:** Backup fails with "mysqldump not found"

**Solutions:**
1. Ensure MySQL bin directory is in PATH:
   - **Windows:** Add `C:\Program Files\MySQL\MySQL Server 8.0\bin` to PATH
   - **macOS:** Add `/usr/local/mysql/bin` to PATH

2. Or specify full path:
   ```python
   cmd = ['/usr/local/mysql/bin/mysqldump', ...]
   ```

## Performance Optimization

### Enable Query Cache (MySQL 5.7 and earlier)

```sql
SET GLOBAL query_cache_type = 1;
SET GLOBAL query_cache_size = 268435456;  # 256MB
```

### Index Optimization

The database automatically creates indexes on:
- `users.username` - For login lookups
- `users.role` - For role-based access
- `test_results.user_id` - For user filtering
- `test_results.test_case_id` - For test case filtering
- `test_stage_results.test_result_id` - For result lookups
- `audit_log.user_id` - For audit trail filtering

### Monitor Slow Queries

Enable slow query log:
```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
```

## Maintenance Tasks

### Regular Backups

Create automated backups:
```python
from data.database_utils import DatabaseUtilities
import schedule
import time

def backup_job():
    utils = DatabaseUtilities()
    utils.create_backup()

schedule.every().day.at("02:00").do(backup_job)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Optimize Tables (Weekly)

```bash
python -c "from data.database_utils import DatabaseUtilities; DatabaseUtilities().vacuum_database()"
```

### Check Integrity (Monthly)

```bash
python health_checker.py
```

### Archive Old Data (Monthly)

```python
from data.database_utils import DatabaseUtilities

utils = DatabaseUtilities()
utils.delete_old_test_results(days=90)
utils.delete_old_audit_logs(days=180)
```

## Security Considerations

1. **Change Default Passwords:** Immediately change passwords for admin, manager, and tester users
2. **Use Strong Passwords:** Minimum 12 characters with mixed case and numbers
3. **Limit Network Access:** Only allow local connections unless needed
4. **Regular Backups:** Maintain automated daily backups
5. **Audit Logging:** Review audit logs regularly for suspicious activity
6. **Database Permissions:** Create dedicated MySQL user with minimal required privileges

## Migration from SQLite

If migrating existing data from SQLite:

```python
import sqlite3
import mysql.connector

# Read from SQLite
sqlite_conn = sqlite3.connect('old_database.db')
sqlite_cursor = sqlite_conn.cursor()

# Write to MySQL
mysql_conn = mysql.connector.connect(host='localhost', user='root', password='password', database='pcb_testing')
mysql_cursor = mysql_conn.cursor()

# Export and import tables
# (Use specialized migration scripts for production)
```

## Support and Documentation

- MySQL Documentation: https://dev.mysql.com/doc/
- Python MySQL Connector: https://dev.mysql.com/doc/connector-python/en/
- Application Database API: See QUICK_REFERENCE.py

---

**Last Updated:** December 11, 2025
**Version:** MySQL 1.0

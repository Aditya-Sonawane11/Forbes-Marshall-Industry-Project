# SQL Database Setup Guide

## Overview
The PCB Testing Automation System now uses an enhanced SQL database (SQLite3) with comprehensive schema, audit logging, and data management features.

## What's New

### Database Enhancements
✅ **Normalized Schema** - Properly structured tables with relationships
✅ **Enhanced Audit Logging** - Track all user actions
✅ **Statistics Tracking** - Auto-calculated pass rates and test metrics
✅ **Multi-Stage Support** - Full support for test sequences with individual stage results
✅ **Better Data Integrity** - Foreign key constraints and cascading deletes
✅ **Performance Indexes** - Optimized query performance
✅ **Data Export** - Export to CSV and JSON formats
✅ **Backup & Recovery** - Built-in backup and restore functionality

## Database Structure

### Core Tables
1. **users** - User accounts and authentication
2. **test_cases** - Test definitions and parameters
3. **test_stages** - Individual stages within tests
4. **test_results** - Test execution results
5. **test_stage_results** - Individual stage results
6. **jig_diagrams** - Visual test point references
7. **communication_config** - Serial port settings

### Supporting Tables
8. **test_statistics** - Aggregated test metrics
9. **audit_log** - User action tracking

For detailed table structures, see `DATABASE_DOCUMENTATION.md`

## Installation & Setup

### 1. Database Initialization
The database is automatically created on first run with default tables and users.

```python
from data.database import Database

db = Database()
# Tables created automatically
```

### 2. Default Users
```
Username: admin      Password: admin123    Role: Admin
Username: manager    Password: manager123  Role: Manager
Username: tester     Password: tester123   Role: Tester
```

**IMPORTANT**: Change these passwords after first login!

## Basic Usage

### User Authentication
```python
from data.database import Database

db = Database()
role, user_id = db.authenticate_user('admin', 'admin123')
if role:
    print(f"Logged in as {role}")
else:
    print("Authentication failed")
```

### Creating Test Cases
```python
# Create a test case
test_case_id = db.save_test_case(
    name='PCB Type-A Test',
    description='Standard test for Type-A PCBs',
    voltage_min=4.5, voltage_max=5.5,
    current_min=0.1, current_max=1.0,
    resistance_min=90, resistance_max=110,
    created_by=1  # user_id
)

# Add stages to test case
stage_id = db.save_test_stage(
    test_case_id=test_case_id,
    stage_number=1,
    stage_name='Initial Voltage Test',
    voltage_min=4.5, voltage_max=5.5,
    current_min=0.1, current_max=0.5,
    resistance_min=90, resistance_max=110
)
```

### Recording Test Results
```python
# Start a test
result_id = db.save_test_result(
    test_case_id=test_case_id,
    user_id=user_id,
    pcb_serial_number='PCB-001-2024',
    status='In Progress'
)

# Record stage results
stage_result_id = db.save_stage_result(
    test_result_id=result_id,
    stage_id=stage_id,
    voltage_measured=5.0,
    current_measured=0.35,
    resistance_measured=100.5,
    status='Pass'
)

# Complete the test
db.update_test_result_status(
    test_result_id=result_id,
    status='Pass',
    overall_pass=True
)

# Update statistics
db.update_test_statistics(test_case_id)
```

### Retrieving Data
```python
# Get all test cases
test_cases = db.get_test_cases()

# Get test results for a user
results = db.get_test_results(user_id=1)

# Get test results for a test case
results = db.get_test_results(test_case_id=1)

# Get stages for a test case
stages = db.get_test_stages(test_case_id=1)

# Get stage results for a test
stage_results = db.get_stage_results(test_result_id=1)

# Get statistics
stats = db.get_test_statistics(test_case_id=1)
```

## Advanced Features

### Backup & Recovery

#### Create Backup
```python
from data.database_utils import DatabaseUtilities

utils = DatabaseUtilities()
backup_path = utils.create_backup()
print(f"Backup created at: {backup_path}")

# Custom backup name
backup_path = utils.create_backup('custom_backup_name.db')
```

#### List Available Backups
```python
backups = utils.list_backups()
for backup in backups:
    print(f"{backup['name']} - {backup['size_mb']} MB - {backup['created']}")
```

#### Restore from Backup
```python
utils.restore_backup('/path/to/backup.db')
```

### Database Maintenance

#### Check Integrity
```python
integrity_result = utils.check_integrity()
if integrity_result['status'] == 'ok':
    print("Database is healthy")
```

#### Optimize Database
```python
utils.vacuum_database()
```

#### Get Statistics
```python
stats = utils.get_database_stats()
print(f"Total users: {stats['users']}")
print(f"Total test results: {stats['test_results']}")
print(f"Database size: {stats['db_size_mb']} MB")
```

### Data Export

#### Export Table to CSV
```python
csv_file = utils.export_table_to_csv('test_results')
```

#### Export Detailed Test Results
```python
csv_file = utils.export_test_results_detailed()
# Includes test cases, testers, stage results, and measurements
```

#### Generate Report
```python
report = utils.generate_summary_report()
print(f"Total tests: {report['total_tests']}")
print(f"Pass rate: {report['overall_pass_rate']:.2f}%")

# Export as JSON
json_file = utils.export_report_to_json()
```

### Audit Logging

All user actions are automatically logged:

```python
# View audit log
audit_log = db.get_audit_log(user_id=1, limit=50)
for entry in audit_log:
    print(f"{entry['timestamp']}: {entry['action']} - {entry['entity_type']}")

# Manual logging
db.log_action(
    user_id=1,
    action='Created test case',
    entity_type='test_case',
    entity_id=5
)
```

### Data Retention & Cleanup

```python
# Delete test results older than 2 years
deleted = utils.delete_old_test_results(days=730)
print(f"Deleted {deleted} old test results")

# Delete audit logs older than 3 years
deleted = utils.delete_old_audit_logs(days=1095)
print(f"Deleted {deleted} old audit log entries")

# Optimize database after cleanup
utils.vacuum_database()
```

## File Locations

```
Forbes Marshall/
├── pcb_testing.db                 # Main database file
├── data/
│   ├── database.py               # Database class
│   ├── database_utils.py         # Utility functions
│   └── __init__.py
├── database_schema.sql           # SQL schema (reference)
└── docs/
    └── DATABASE_DOCUMENTATION.md # Full documentation
```

### Backups
Backups are stored in:
```
Forbes Marshall/backups/
├── pcb_testing_backup_20240101_120000.db
├── pcb_testing_backup_20240102_120000.db
└── ...
```

### Exports
CSV and JSON exports are stored in:
```
Forbes Marshall/
├── test_results_export.csv
├── system_report_20240101_120000.json
└── ...
```

## Performance Tips

1. **Regular Backups**: Create daily backups automatically
2. **Periodic Cleanup**: Run data cleanup monthly for old test results
3. **Database Vacuum**: Run optimization after cleanup operations
4. **Index Management**: All critical columns are already indexed
5. **Batch Operations**: Use transactions for multiple inserts

## Security Considerations

- ✅ Passwords are hashed with bcrypt
- ✅ All queries use parameterized statements (SQL injection protection)
- ✅ Audit trail tracks all user actions
- ✅ Role-based access control (enforced at application level)
- ✅ Foreign key constraints prevent orphaned records
- ✅ Regular backups ensure data recovery

## Troubleshooting

### Database Locked Error
```python
# Close and reconnect
db.close()
db.connect()
```

### Slow Queries
1. Check for missing indexes (see database_schema.sql)
2. Archive old results using cleanup functions
3. Run VACUUM to optimize file size

### Data Recovery
1. List available backups: `utils.list_backups()`
2. Restore from backup: `utils.restore_backup(backup_path)`
3. Verify integrity: `utils.check_integrity()`

## Migration from Previous Version

If upgrading from an older system:

1. Automatic migration on first run
2. Check `database_schema.sql` for schema
3. Run consistency check: `utils.check_integrity()`
4. Verify data in UI
5. Keep old backup just in case

## API Reference

See `DATABASE_DOCUMENTATION.md` for complete API reference including:
- All table schemas
- Relationship diagrams
- Complete method signatures
- Performance notes
- Data retention policies

## Support

For issues or questions:
1. Check `DATABASE_DOCUMENTATION.md` for detailed reference
2. Review code examples in this guide
3. Check audit logs for action history
4. Restore from backup if needed

---

## Quick Start Example

```python
from data.database import Database
from data.database_utils import DatabaseUtilities

# Initialize database
db = Database()

# Authenticate
role, user_id = db.authenticate_user('tester', 'tester123')

# Get test cases
test_cases = db.get_test_cases()

# Create test result
result_id = db.save_test_result(
    test_case_id=1,
    user_id=user_id,
    pcb_serial_number='PCB-TEST-001',
    status='Pass'
)

# Save stage result
db.save_stage_result(
    test_result_id=result_id,
    stage_id=1,
    voltage_measured=5.0,
    current_measured=0.5,
    resistance_measured=100,
    status='Pass'
)

# Update and export
db.update_test_statistics(test_case_id=1)

utils = DatabaseUtilities()
csv_file = utils.export_test_results_detailed()
print(f"Results exported to: {csv_file}")
```

Enjoy your enhanced database system! 🚀

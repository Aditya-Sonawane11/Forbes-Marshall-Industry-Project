# SQL Database Documentation
## PCB Testing Automation System

### Overview
The PCB Testing Automation System uses SQLite3 as the primary database backend. This document describes all tables, relationships, and usage patterns.

---

## Database Tables

### 1. **users**
Stores user account information with role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user identifier |
| username | TEXT | UNIQUE, NOT NULL | Login username |
| password_hash | TEXT | NOT NULL | Bcrypt hashed password |
| role | TEXT | CHECK(role IN ('Admin', 'Manager', 'Tester')) | User role |
| email | TEXT | NULL | User email address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |
| is_active | BOOLEAN | DEFAULT 1 | Account status |

**Indexes:**
- `idx_users_username` - For fast username lookups
- `idx_users_role` - For role-based queries

**Default Users:**
```
Admin:    admin / admin123
Manager:  manager / manager123
Tester:   tester / tester123
```

---

### 2. **test_cases**
Defines test specifications and acceptance criteria for PCB testing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Test case identifier |
| name | TEXT | NOT NULL | Test case name |
| description | TEXT | NULL | Detailed description |
| voltage_min | REAL | NOT NULL | Minimum voltage threshold |
| voltage_max | REAL | NOT NULL | Maximum voltage threshold |
| current_min | REAL | NOT NULL | Minimum current threshold |
| current_max | REAL | NOT NULL | Maximum current threshold |
| resistance_min | REAL | NOT NULL | Minimum resistance threshold |
| resistance_max | REAL | NOT NULL | Maximum resistance threshold |
| created_by | INTEGER | FK users(id) | Creator user ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- `idx_test_cases_created_by`

---

### 3. **test_stages**
Individual stages within a test case for multi-stage testing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Stage identifier |
| test_case_id | INTEGER | FK test_cases(id) ON DELETE CASCADE | Parent test case |
| stage_number | INTEGER | NOT NULL | Sequential stage number |
| stage_name | TEXT | NOT NULL | Stage name/description |
| description | TEXT | NULL | Detailed stage description |
| voltage_min | REAL | NULL | Stage voltage min |
| voltage_max | REAL | NULL | Stage voltage max |
| current_min | REAL | NULL | Stage current min |
| current_max | REAL | NULL | Stage current max |
| resistance_min | REAL | NULL | Stage resistance min |
| resistance_max | REAL | NULL | Stage resistance max |
| duration_seconds | INTEGER | NULL | Stage execution duration |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Update timestamp |

**Constraints:**
- UNIQUE(test_case_id, stage_number) - No duplicate stage numbers per test case

**Indexes:**
- `idx_test_stages_test_case_id`

---

### 4. **test_results**
Records of executed tests with overall results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Test result identifier |
| test_case_id | INTEGER | FK test_cases(id) | Test case used |
| user_id | INTEGER | FK users(id) | Tester who ran test |
| pcb_serial_number | TEXT | NULL | PCB serial/batch number |
| status | TEXT | CHECK(status IN ('Pass', 'Fail', 'In Progress')) | Overall test status |
| overall_pass | BOOLEAN | NULL | Pass/Fail flag |
| start_time | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Test start time |
| end_time | TIMESTAMP | NULL | Test completion time |
| notes | TEXT | NULL | Test notes/comments |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- `idx_test_results_user_id`
- `idx_test_results_test_case_id`
- `idx_test_results_start_time`

---

### 5. **test_stage_results**
Detailed results for each stage within a test.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Stage result identifier |
| test_result_id | INTEGER | FK test_results(id) ON DELETE CASCADE | Parent test result |
| stage_id | INTEGER | FK test_stages(id) | Stage definition |
| voltage_measured | REAL | NULL | Actual voltage reading |
| current_measured | REAL | NULL | Actual current reading |
| resistance_measured | REAL | NULL | Actual resistance reading |
| status | TEXT | CHECK(status IN ('Pass', 'Fail', 'Not Run')) | Stage status |
| failure_reason | TEXT | NULL | Failure description if failed |
| start_time | TIMESTAMP | NULL | Stage start time |
| end_time | TIMESTAMP | NULL | Stage completion time |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |

**Indexes:**
- `idx_test_stage_results_test_result_id`

---

### 6. **jig_diagrams**
References to visual PCB jig diagrams for testers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Diagram identifier |
| test_case_id | INTEGER | FK test_cases(id) ON DELETE SET NULL | Associated test case |
| diagram_name | TEXT | NOT NULL | Display name |
| file_path | TEXT | NOT NULL | Path to diagram file |
| description | TEXT | NULL | Diagram description |
| uploaded_by | INTEGER | FK users(id) | Uploader user ID |
| uploaded_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Upload timestamp |

**Indexes:**
- `idx_jig_diagrams_test_case_id`

---

### 7. **communication_config**
Serial/COM port configuration settings for hardware communication.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Configuration identifier |
| config_name | TEXT | NOT NULL | Configuration name |
| com_port | TEXT | NULL | Serial port (e.g., COM1) |
| baud_rate | INTEGER | DEFAULT 9600 | Bits per second |
| data_bits | INTEGER | DEFAULT 8 | Data bits (5-8) |
| stop_bits | INTEGER | DEFAULT 1 | Stop bits (1-2) |
| parity | TEXT | DEFAULT 'None' | Parity (None, Odd, Even) |
| timeout_seconds | INTEGER | DEFAULT 5 | Communication timeout |
| created_by | INTEGER | FK users(id) | Creator user ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Update time |

---

### 8. **test_statistics**
Aggregated statistics for test cases (auto-updated).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Statistics record ID |
| test_case_id | INTEGER | FK test_cases(id) ON DELETE CASCADE | Test case |
| total_tests | INTEGER | DEFAULT 0 | Total tests executed |
| passed_tests | INTEGER | DEFAULT 0 | Number passed |
| failed_tests | INTEGER | DEFAULT 0 | Number failed |
| pass_rate | REAL | DEFAULT 0.0 | Pass rate percentage |
| last_updated | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

**Constraints:**
- UNIQUE(test_case_id) - One record per test case

---

### 9. **audit_log**
Audit trail of all user actions for compliance and debugging.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Log entry ID |
| user_id | INTEGER | FK users(id) | User who performed action |
| action | TEXT | NOT NULL | Action description |
| entity_type | TEXT | NULL | Type of entity affected |
| entity_id | INTEGER | NULL | ID of affected entity |
| old_values | TEXT | NULL | Previous values (JSON) |
| new_values | TEXT | NULL | New values (JSON) |
| timestamp | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Action timestamp |

**Indexes:**
- `idx_audit_log_user_id`
- `idx_audit_log_timestamp`

---

## Relationships Diagram

```
users (1) ──── (N) test_cases
  │
  │
  ├─── (1) ──── (N) test_results
  │                    │
  │                    └─── (1) ──── (N) test_stage_results
  │
  ├─── (1) ──── (N) jig_diagrams
  │
  ├─── (1) ──── (N) communication_config
  │
  └─── (1) ──── (N) audit_log

test_cases (1) ──── (N) test_stages
                          │
                          └─── (1) ──── (N) test_stage_results

test_cases (1) ──── (1) test_statistics
test_cases (1) ──── (N) jig_diagrams
```

---

## Key Database Operations

### User Management
```python
# Authenticate user
db.authenticate_user(username, password)  # Returns (role, user_id)

# Create new user
db.create_user(username, password, role, email)

# Get user info
db.get_user_by_id(user_id)
```

### Test Case Management
```python
# Save test case
test_case_id = db.save_test_case(name, description, v_min, v_max, c_min, c_max, r_min, r_max, created_by)

# Get test cases
cases = db.get_test_cases()

# Delete test case (cascades to stages, results, diagrams, statistics)
db.delete_test_case(test_case_id)
```

### Test Stage Management
```python
# Save stage
stage_id = db.save_test_stage(test_case_id, stage_number, name, description, v_min, v_max, c_min, c_max, r_min, r_max)

# Get stages for test case
stages = db.get_test_stages(test_case_id)
```

### Test Result Recording
```python
# Start a test
result_id = db.save_test_result(test_case_id, user_id, pcb_serial, 'In Progress')

# Record stage results
stage_result_id = db.save_stage_result(result_id, stage_id, v_measured, c_measured, r_measured, 'Pass')

# Complete test
db.update_test_result_status(result_id, 'Pass', overall_pass=True)

# Update statistics
db.update_test_statistics(test_case_id)
```

### Data Export
```python
# Export results to CSV
columns, data = db.export_test_results_to_csv(test_case_id)
```

---

## Performance Considerations

1. **Indexes**: All foreign keys and frequently searched columns are indexed
2. **Cascading Deletes**: Deleting test cases automatically removes related data
3. **Statistics Cache**: Test statistics are maintained for quick dashboard queries
4. **Batch Operations**: Use transactions for multi-record inserts/updates
5. **Query Optimization**: All queries use parameterized statements to prevent SQL injection

---

## Backup and Maintenance

### Regular Backups
```bash
# Backup database
cp pcb_testing.db pcb_testing_backup_YYYY-MM-DD.db

# Restore from backup
cp pcb_testing_backup_YYYY-MM-DD.db pcb_testing.db
```

### Database Integrity Check
```python
# Run PRAGMA integrity_check
db.cursor.execute('PRAGMA integrity_check')
result = db.cursor.fetchall()
```

### Vacuum (Optimize)
```python
# Optimize database file size
db.cursor.execute('VACUUM')
```

---

## Data Retention Policy

- **Test Results**: Keep for 2 years minimum (compliance)
- **Audit Log**: Keep for 3 years minimum (regulatory)
- **Test Cases**: Permanent (reference data)
- **Statistics**: Aggregated monthly for long-term retention

---

## Security Features

1. **Password Hashing**: Bcrypt with salt
2. **SQL Injection Prevention**: Parameterized queries throughout
3. **Audit Trail**: All user actions logged
4. **Role-Based Access**: Enforced at application level
5. **Data Validation**: Type checking and constraints at DB level

---

## Migration from Legacy System

If migrating from a previous system:

1. Export legacy data to CSV
2. Write import script to populate new tables
3. Validate data integrity
4. Run statistics update
5. Test all features before switching

---

## Troubleshooting

### Database Locked
```python
# Close connections and retry
db.close()
db.connect()
```

### Slow Queries
- Check index usage with `EXPLAIN QUERY PLAN`
- Add missing indexes
- Archive old test results

### Data Corruption
- Run `PRAGMA integrity_check`
- Restore from backup if needed

---

## Support & Contact

For database-related issues, refer to the SQLite documentation or contact the development team.

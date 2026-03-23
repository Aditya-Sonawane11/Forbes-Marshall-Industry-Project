# Detailed Prompt for PowerPoint Presentation

## Title: PCB Testing Automation System — Forbes Marshall

> Use this prompt with any AI presentation tool (Gamma, Beautiful.ai, ChatGPT PPT generator, Google Slides + Gemini, etc.) to generate a professional, visually rich presentation.

---

## Prompt

Create a **professional, modern PowerPoint presentation** (20–25 slides) for the **PCB Testing Automation System** developed for **Forbes Marshall**. Use a **corporate blue (#2B5A8C) and dark (#2A2A2A) color theme** with clean visuals, icons, and diagrams. The presentation is intended for a **college project evaluation / industry review panel**.

---

### Slide-by-Slide Outline

---

#### **Slide 1 — Title Slide**
- **Title:** PCB Testing Automation System
- **Subtitle:** Automated Multi-Stage PCB Quality Assurance Platform
- **Organization:** Forbes Marshall (Industry Project)
- **Date:** March 2026
- Add Forbes Marshall logo placeholder

---

#### **Slide 2 — Table of Contents**
List all sections:
1. Problem Statement
2. Project Objectives
3. Technology Stack
4. System Architecture
5. Database Schema
6. User Roles & Access Control
7. Core Features (Phase 1–4)
8. UI Screenshots / Mockups
9. Serial Communication & Hardware Integration
10. Testing & Quality Assurance
11. Future Scope
12. Conclusion

---

#### **Slide 3 — Problem Statement**
- Manual PCB testing is error-prone, slow, and lacks traceability
- No centralized system for recording test outcomes
- Different operators may apply inconsistent testing parameters
- No role-based control over test administration
- Lack of hardware integration for automated data capture

---

#### **Slide 4 — Project Objectives**
- Build a desktop application to automate PCB testing workflows
- Implement role-based access control (Admin, Manager, Tester)
- Create multi-stage test sequences with configurable parameters
- Integrate serial communication (COM port) for real-time PCB data capture
- Store all test results in a MySQL database for traceability
- Support barcode scanner input for PCB identification
- Provide export, statistics, and audit logging capabilities

---

#### **Slide 5 — Technology Stack**
Present as a visual stack/grid:

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Language         | Python 3.8+                         |
| GUI Framework    | CustomTkinter (Modern Tkinter)      |
| Database         | MySQL 8.0                           |
| DB Connector     | mysql-connector-python              |
| Image Handling   | Pillow (PIL)                        |
| Serial Comm      | PySerial                            |
| Password Hashing | bcrypt                              |
| Packaging        | PyInstaller                         |

---

#### **Slide 6 — System Architecture**
Show a layered architecture diagram:

```
┌────────────────────────────────────────────────┐
│              Presentation Layer                │
│   (CustomTkinter GUI — Login, Dashboard, etc.) │
├────────────────────────────────────────────────┤
│              Business Logic Layer              │
│   (Test Execution, Stage Sequencing,           │
│    Parameter Validation, Role Checks)          │
├────────────────────────────────────────────────┤
│              Data Access Layer                 │
│   (database.py — 700+ lines, 40+ methods)     │
│   (database_utils.py — Backup, Export, Audit)  │
├────────────────────────────────────────────────┤
│              Database Layer                    │
│   (MySQL 8.0 — pcb_testing database)          │
│   (9 Tables, Indexed, Foreign Keys)           │
├────────────────────────────────────────────────┤
│              Hardware Interface Layer          │
│   (PySerial — COM Port Communication)         │
│   (USB Barcode Scanner — Keyboard Emulation)  │
└────────────────────────────────────────────────┘
```

---

#### **Slide 7 — Database Schema Overview**
Show an **Entity-Relationship (ER) diagram** with 9 tables:

**Tables:**

1. **users** — Stores user accounts with bcrypt-hashed passwords
   - `id` (PK), `username` (UNIQUE), `password_hash`, `role` (Admin/Manager/Tester), `email`, `created_at`, `is_active`

2. **test_cases** — Defines test profiles with min/max thresholds
   - `id` (PK), `name`, `description`, `voltage_min`, `voltage_max`, `current_min`, `current_max`, `resistance_min`, `resistance_max`, `created_by` (FK → users), `created_at`, `updated_at`

3. **test_stages** — Individual stages within a multi-stage test
   - `id` (PK), `test_case_id` (FK → test_cases), `stage_number`, `stage_name`, `description`, voltage/current/resistance min/max, `duration_seconds`, `created_at`, `updated_at`
   - UNIQUE constraint on (`test_case_id`, `stage_number`)

4. **test_results** — Overall test execution records
   - `id` (PK), `test_case_id` (FK → test_cases), `user_id` (FK → users), `pcb_serial_number`, `status` (Pass/Fail/In Progress), `overall_pass`, `start_time`, `end_time`, `notes`

5. **test_stage_results** — Per-stage measured values and outcomes
   - `id` (PK), `test_result_id` (FK → test_results), `stage_id` (FK → test_stages), `voltage_measured`, `current_measured`, `resistance_measured`, `status` (Pass/Fail/Not Run), `failure_reason`, `start_time`, `end_time`

6. **communication_config** — Serial port configuration profiles
   - `id` (PK), `config_name`, `com_port`, `baud_rate`, `data_bits`, `stop_bits`, `parity`, `timeout_seconds`, `created_by` (FK → users)

7. **jig_diagrams** — Test jig reference images
   - `id` (PK), `test_case_id` (FK → test_cases), `diagram_name`, `file_path`, `description`, `uploaded_by` (FK → users)

8. **test_statistics** — Aggregated pass/fail stats per test case
   - `id` (PK), `test_case_id` (FK → test_cases, UNIQUE), `total_tests`, `passed_tests`, `failed_tests`, `pass_rate`

9. **audit_log** — Complete activity audit trail
   - `id` (PK), `user_id` (FK → users), `action`, `entity_type`, `entity_id`, `old_values`, `new_values`, `timestamp`

---

#### **Slide 8 — Database ER Diagram (Visual)**
Draw an ER diagram showing all relationships:

```
users ──────┬──── 1:N ────── test_cases
            │                     │
            │                     ├── 1:N ──── test_stages
            │                     │
            │                     ├── 1:N ──── test_results ── 1:N ── test_stage_results
            │                     │
            │                     ├── 1:N ──── jig_diagrams
            │                     │
            │                     └── 1:1 ──── test_statistics
            │
            ├── 1:N ────── communication_config
            │
            ├── 1:N ────── test_results
            │
            └── 1:N ────── audit_log
```

Show **foreign key arrows** and **cardinality notation** (1:N, 1:1).

---

#### **Slide 9 — Database Indexes**
Show performance optimization indexes:

| Index Name                          | Table             | Column(s)       |
|-------------------------------------|-------------------|-----------------|
| idx_users_username                  | users             | username        |
| idx_users_role                      | users             | role            |
| idx_test_results_user_id            | test_results      | user_id         |
| idx_test_results_test_case_id       | test_results      | test_case_id    |
| idx_test_results_start_time         | test_results      | start_time      |
| idx_test_stage_results_test_result  | test_stage_results| test_result_id  |
| idx_test_stages_test_case_id        | test_stages       | test_case_id    |
| idx_jig_diagrams_test_case_id       | jig_diagrams      | test_case_id    |
| idx_audit_log_user_id               | audit_log         | user_id         |
| idx_audit_log_timestamp             | audit_log         | timestamp       |

---

#### **Slide 10 — User Roles & Access Control**
Show a matrix/table:

| Feature                   | Admin | Manager | Tester |
|---------------------------|:-----:|:-------:|:------:|
| Login                     |  ✅   |   ✅    |  ✅    |
| Run Tests                 |  ✅   |   ✅    |  ✅    |
| View Test Results         |  ✅   |   ✅    |  ✅    |
| Create/Edit Test Cases    |  ✅   |   ✅    |  ❌    |
| Build Multi-Stage Tests   |  ✅   |   ✅    |  ❌    |
| View Jig Diagrams         |  ✅   |   ✅    |  ✅    |
| Upload Jig Diagrams       |  ✅   |   ❌    |  ❌    |
| Configure COM Ports       |  ✅   |   ❌    |  ❌    |
| User Management           |  ✅   |   ❌    |  ❌    |
| Export Data               |  ✅   |   ✅    |  ❌    |

Role hierarchy: Admin (Level 3) > Manager (Level 2) > Tester (Level 1)

---

#### **Slide 11 — Phase 1: Core Testing**
- User authentication with bcrypt password hashing
- Role-based login and dashboard
- Start Test window with manual parameter entry
- Pass/Fail logic based on voltage (4.5–5.5V), current (0.1–1.0A), resistance (90–110Ω)
- Results stored in MySQL with timestamp tracking

---

#### **Slide 12 — Phase 2: Test Management**
- Results History with advanced filtering (by date, status, user, PCB serial)
- CSV export of test results
- Test Case Editor — create custom test profiles with configurable thresholds
- Statistics dashboard with pass rates
- Role-based visibility of results

---

#### **Slide 13 — Phase 3: Advanced Multi-Stage Testing**
- Stage Builder — define multi-stage test sequences
- Each stage has its own voltage/current/resistance thresholds and duration
- Advanced Test Runner — executes stages sequentially
- Real-time progress tracking with live stage indicators
- Per-stage failure reporting with detailed failure reasons
- Custom workflows for different PCB types

---

#### **Slide 14 — Phase 4: Hardware Integration**
- Serial Communication via PySerial (COM port)
- Expected data format from PCB: `V:5.0,C:0.5,R:100.0`
- Admin-controlled serial port configuration (baud rate, data bits, stop bits, parity, timeout)
- Automatic vs Manual test mode switching
- USB Barcode Scanner support (keyboard emulation)
- Auto-focus PCB ID capture on scan
- Jig Diagram Viewer — upload and view test fixture reference images (PNG, JPG, GIF, BMP)

---

#### **Slide 15 — Application UI Flow**
Show a flowchart:

```
Login Screen
    │
    ▼
Dashboard (Role-Based Menu)
    │
    ├── Start Test ──────────► Run Single Test ──► Save Result
    ├── Advanced Test ───────► Multi-Stage Execution ──► Save All Stage Results
    ├── Test Case Editor ────► Create/Edit Test Profiles
    ├── Stage Builder ───────► Define Multi-Stage Sequences
    ├── Results History ─────► View/Filter/Export Results
    ├── Jig Diagram Viewer ──► Upload/View Reference Images
    └── Communication Config ► Configure COM Port Settings
```

---

#### **Slide 16 — Project Structure**
Show as a tree diagram:

```
PCB Testing System/
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── config/
│   └── config.py                 # MySQL & app configuration
├── data/
│   ├── database.py               # 700+ lines, 40+ API methods
│   └── database_utils.py         # Backup, export, maintenance
├── ui/
│   ├── login_window.py           # Authentication screen
│   ├── dashboard.py              # Main navigation hub
│   ├── start_test.py             # Single test execution
│   ├── advanced_test.py          # Multi-stage test runner
│   ├── results_history.py        # Test result viewer
│   ├── test_case_editor.py       # Test profile manager
│   ├── stage_builder.py          # Multi-stage builder
│   ├── jig_diagram_viewer.py     # Jig image viewer
│   └── communication_config.py   # Serial port settings
├── utils/
│   └── serial_handler.py         # PySerial communication
├── assets/
│   ├── logo.png                  # Forbes Marshall logo
│   └── diagrams/                 # Jig diagram images
└── docs/                         # Documentation
```

---

#### **Slide 17 — Key Database Queries**
Show a sample comprehensive query (from complete-table.sql) that JOINs all 9 tables:

```sql
SELECT tr.id, tr.pcb_serial_number, tr.status,
       u.username, u.role,
       tc.name AS test_case_name,
       ts.stage_name, tsr.voltage_measured,
       tsr.current_measured, tsr.resistance_measured,
       tsr.status AS stage_status,
       tsx.pass_rate
FROM test_results tr
JOIN users u ON tr.user_id = u.id
JOIN test_cases tc ON tr.test_case_id = tc.id
LEFT JOIN test_stage_results tsr ON tsr.test_result_id = tr.id
LEFT JOIN test_stages ts ON ts.id = tsr.stage_id
LEFT JOIN test_statistics tsx ON tsx.test_case_id = tc.id
ORDER BY tr.start_time DESC;
```

Highlight: 40+ database API methods covering all CRUD operations.

---

#### **Slide 18 — Health Check & Verification Tools**
- `health_checker.py` — Automated system diagnostics
  - Database connectivity, table integrity, authentication tests, CRUD validation, query performance benchmarking
- `api_endpoint_checker.py` — Tests 28+ API endpoints
- `init_mysql.py` — One-command database initialization
- All tools generate JSON reports for audit

---

#### **Slide 19 — Security Features**
- bcrypt password hashing (no plain-text storage)
- Role-based access control (RBAC) at UI and data layer
- Foreign key constraints for data integrity
- Audit logging — every action tracked with old/new values
- Input validation on all test parameters
- Session management with logout functionality

---

#### **Slide 20 — Backup & Data Management**
- Automated database backup system
- CSV export of test results
- Database integrity checks
- Data archival capabilities
- JSON report generation for health and API checks

---

#### **Slide 21 — Test Parameter Validation**
Show validation logic with visual ranges:

| Parameter   | Min   | Max    | Unit |
|-------------|-------|--------|------|
| Voltage     | 4.5   | 5.5    | V    |
| Current     | 0.1   | 1.0    | A    |
| Resistance  | 90    | 110    | Ω    |

- Measured values compared against configurable thresholds
- Each stage can have independent thresholds
- Automatic Pass/Fail determination

---

#### **Slide 22 — Challenges & Solutions**

| Challenge                                 | Solution                                    |
|-------------------------------------------|---------------------------------------------|
| Reliable serial communication             | PySerial with configurable timeout & retry  |
| Database migration (SQLite → MySQL)       | Complete rewrite with mysql-connector       |
| Multi-stage test sequencing               | Stage Builder with ordered execution engine |
| Role-based UI rendering                   | Dynamic widget creation based on role level |
| Cross-platform packaging                  | PyInstaller with resource path resolution   |
| Real-time data capture from hardware      | Threaded serial reading with data parsing   |

---

#### **Slide 23 — Future Scope**
- Web-based dashboard for remote monitoring
- IoT sensor integration for environmental data (temperature, humidity)
- Machine learning for predictive test failure analysis
- Cloud database deployment (AWS RDS / Azure MySQL)
- REST API for third-party integration
- Automated test scheduling and batch execution
- Mobile companion app for notifications
- Multi-language support

---

#### **Slide 24 — Conclusion**
- Successfully built a complete PCB testing automation platform
- 9-table MySQL database with 40+ API methods
- 4-phase development covering core testing through hardware integration
- Role-based access for Admin, Manager, and Tester workflows
- Serial communication integration for real-time data capture
- Production-ready with health checks, backups, and audit logging

---

#### **Slide 25 — Thank You / Q&A**
- Thank you for your attention
- **Project:** PCB Testing Automation System
- **Organization:** Forbes Marshall
- **Tech Stack:** Python + CustomTkinter + MySQL + PySerial
- Contact information placeholder
- Q&A

---

## Presentation Design Notes

- **Primary Color:** #2B5A8C (Corporate Blue)
- **Secondary Color:** #2A2A2A (Dark Background)
- **Accent Color:** #4CAF50 (Green for Pass), #F44336 (Red for Fail)
- **Font:** Segoe UI or Inter
- **Style:** Modern, minimal, with icons and diagrams
- **Include:** Forbes Marshall logo on every slide header
- **Slide transitions:** Subtle fade or slide
- **Charts:** Use pie charts for pass/fail ratios, bar charts for statistics


also use the below part


# PCB Testing Automation System — Forbes Marshall

> Automated multi-stage PCB quality assurance platform with role-based access control, serial hardware integration, and comprehensive test traceability.

---

## Overview

The **PCB Testing Automation System** is a desktop application built for **Forbes Marshall** to automate and standardize PCB (Printed Circuit Board) testing workflows. It replaces manual testing processes with a centralized, configurable, and traceable system backed by a **MySQL database** with **9 normalized tables** and **40+ API methods**.

---

## Key Highlights

- **4-Phase Development** — Core Testing → Test Management → Advanced Multi-Stage Testing → Hardware Integration
- **Role-Based Access Control** — Admin, Manager, Tester with hierarchical permissions
- **MySQL Database** — 9 tables, 10+ indexes, foreign key constraints, audit logging
- **Serial Communication** — Real-time PCB data capture via COM port (PySerial)
- **Barcode Scanner** — USB barcode scanner support for automatic PCB identification
- **Modern GUI** — CustomTkinter-based dark-themed interface

---

## Technology Stack

| Layer            | Technology                            |
|------------------|---------------------------------------|
| Language         | Python 3.8+                           |
| GUI Framework    | CustomTkinter 5.2.1                   |
| Database         | MySQL 8.0                             |
| DB Connector     | mysql-connector-python 8.2+           |
| Image Handling   | Pillow 10.2+                          |
| Serial Comm      | PySerial 3.5+                         |
| Password Hashing | bcrypt 4.1+                           |
| Packaging        | PyInstaller                           |

---

## Features

### Phase 1 — Core Testing
- User authentication with **bcrypt password hashing**
- Role-based login with dynamic dashboard
- Start Test with manual parameter entry
- Pass/Fail validation for Voltage, Current, and Resistance
- Results stored in MySQL with timestamps

### Phase 2 — Test Management
- Results History with filtering by date, status, user, and PCB serial number
- CSV export of test results
- Test Case Editor — create and manage test profiles with custom thresholds
- Pass rate statistics and tracking
- Role-based result visibility

### Phase 3 — Advanced Multi-Stage Testing
- **Stage Builder** — define ordered multi-stage test sequences
- Each stage has independent voltage/current/resistance thresholds and duration
- **Advanced Test Runner** — sequential stage execution with real-time progress
- Per-stage failure reporting with detailed failure reasons
- Custom workflows for different PCB types

### Phase 4 — Hardware Integration
- Serial Communication via COM port (configurable baud rate, data bits, stop bits, parity, timeout)
- Expected PCB data format: `V:5.0,C:0.5,R:100.0`
- Automatic vs Manual test mode switching
- USB Barcode Scanner support (keyboard emulation mode)
- Jig Diagram Viewer — upload and view test fixture reference images (PNG, JPG, GIF, BMP)
- Admin-controlled communication settings

---

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server 8.0+ (running)

### Steps

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Configure MySQL credentials in config/config.py
#    Edit DB_HOST, DB_USER, DB_PASSWORD, DB_PORT as needed

# 3. Initialize the database (creates tables + default users)
python init_mysql.py

# 4. Verify installation
python health_checker.py

# 5. Run the application
python main.py
```

### Default Credentials

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Admin   | admin     | admin123    |
| Manager | manager   | manager123  |
| Tester  | tester    | tester123   |

---

## Database Schema

The system uses a **MySQL database** (`pcb_testing`) with **9 normalized tables**:

### Tables

| # | Table                  | Purpose                                   | Key Relationships              |
|---|------------------------|-------------------------------------------|--------------------------------|
| 1 | `users`                | User accounts with hashed passwords       | Referenced by most tables      |
| 2 | `test_cases`           | Test profiles with min/max thresholds     | FK → users                     |
| 3 | `test_stages`          | Individual stages in multi-stage tests    | FK → test_cases                |
| 4 | `test_results`         | Overall test execution records            | FK → test_cases, users         |
| 5 | `test_stage_results`   | Per-stage measured values and outcomes     | FK → test_results, test_stages |
| 6 | `communication_config` | Serial port configuration profiles        | FK → users                     |
| 7 | `jig_diagrams`         | Test jig reference images                 | FK → test_cases, users         |
| 8 | `test_statistics`      | Aggregated pass/fail stats per test case  | FK → test_cases (UNIQUE)       |
| 9 | `audit_log`            | Complete activity audit trail             | FK → users                     |

### Entity Relationships

```
users ──────┬── 1:N ── test_cases ──┬── 1:N ── test_stages
            │                       ├── 1:N ── test_results ── 1:N ── test_stage_results
            │                       ├── 1:N ── jig_diagrams
            │                       └── 1:1 ── test_statistics
            ├── 1:N ── communication_config
            ├── 1:N ── test_results
            └── 1:N ── audit_log
```

### Detailed Table Definitions

#### `users`
| Column         | Type             | Constraints                          |
|----------------|------------------|--------------------------------------|
| id             | INT (PK)         | AUTO_INCREMENT                       |
| username       | VARCHAR(255)     | UNIQUE, NOT NULL                     |
| password_hash  | VARCHAR(255)     | NOT NULL (bcrypt)                    |
| role           | ENUM             | 'Admin', 'Manager', 'Tester'        |
| email          | VARCHAR(255)     |                                      |
| created_at     | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP            |
| is_active      | BOOLEAN          | DEFAULT 1                            |

#### `test_cases`
| Column         | Type             | Constraints                          |
|----------------|------------------|--------------------------------------|
| id             | INT (PK)         | AUTO_INCREMENT                       |
| name           | VARCHAR(255)     | NOT NULL                             |
| description    | TEXT             |                                      |
| voltage_min/max| DECIMAL(10,2)    | NOT NULL                             |
| current_min/max| DECIMAL(10,2)    | NOT NULL                             |
| resistance_min/max | DECIMAL(10,2)| NOT NULL                             |
| created_by     | INT (FK)         | → users(id)                          |
| created_at     | TIMESTAMP        | DEFAULT CURRENT_TIMESTAMP            |
| updated_at     | TIMESTAMP        | ON UPDATE CURRENT_TIMESTAMP          |

#### `test_stages`
| Column         | Type             | Constraints                          |
|----------------|------------------|--------------------------------------|
| id             | INT (PK)         | AUTO_INCREMENT                       |
| test_case_id   | INT (FK)         | → test_cases(id) ON DELETE CASCADE   |
| stage_number   | INT              | UNIQUE with test_case_id             |
| stage_name     | VARCHAR(100)     | NOT NULL                             |
| voltage/current/resistance min/max | REAL |                             |
| duration_seconds | INT            |                                      |

#### `test_results`
| Column           | Type           | Constraints                          |
|------------------|----------------|--------------------------------------|
| id               | INT (PK)       | AUTO_INCREMENT                       |
| test_case_id     | INT (FK)       | → test_cases(id)                     |
| user_id          | INT (FK)       | → users(id)                          |
| pcb_serial_number| VARCHAR(100)   |                                      |
| status           | VARCHAR(20)    | 'Pass', 'Fail', 'In Progress'       |
| overall_pass     | BOOLEAN        |                                      |
| start_time       | TIMESTAMP      | DEFAULT CURRENT_TIMESTAMP            |
| end_time         | TIMESTAMP      |                                      |
| notes            | TEXT           |                                      |

#### `test_stage_results`
| Column              | Type         | Constraints                          |
|---------------------|--------------|--------------------------------------|
| id                  | INT (PK)     | AUTO_INCREMENT                       |
| test_result_id      | INT (FK)     | → test_results(id) ON DELETE CASCADE |
| stage_id            | INT (FK)     | → test_stages(id)                    |
| voltage_measured    | REAL         |                                      |
| current_measured    | REAL         |                                      |
| resistance_measured | REAL         |                                      |
| status              | VARCHAR(20)  | 'Pass', 'Fail', 'Not Run'           |
| failure_reason      | TEXT         |                                      |

#### `communication_config`
| Column          | Type          | Constraints                          |
|-----------------|---------------|--------------------------------------|
| id              | INT (PK)      | AUTO_INCREMENT                       |
| config_name     | VARCHAR(100)  | NOT NULL                             |
| com_port        | VARCHAR(10)   |                                      |
| baud_rate       | INT           | DEFAULT 9600                         |
| data_bits       | INT           | DEFAULT 8                            |
| stop_bits       | INT           | DEFAULT 1                            |
| parity          | VARCHAR(10)   | DEFAULT 'None'                       |
| timeout_seconds | INT           | DEFAULT 5                            |
| created_by      | INT (FK)      | → users(id)                          |

#### `jig_diagrams`
| Column        | Type          | Constraints                            |
|---------------|---------------|----------------------------------------|
| id            | INT (PK)      | AUTO_INCREMENT                         |
| test_case_id  | INT (FK)      | → test_cases(id) ON DELETE SET NULL    |
| diagram_name  | VARCHAR(100)  | NOT NULL                               |
| file_path     | VARCHAR(255)  | NOT NULL                               |
| description   | TEXT          |                                        |
| uploaded_by   | INT (FK)      | → users(id)                            |

#### `test_statistics`
| Column        | Type          | Constraints                            |
|---------------|---------------|----------------------------------------|
| id            | INT (PK)      | AUTO_INCREMENT                         |
| test_case_id  | INT (FK)      | → test_cases(id), UNIQUE               |
| total_tests   | INT           | DEFAULT 0                              |
| passed_tests  | INT           | DEFAULT 0                              |
| failed_tests  | INT           | DEFAULT 0                              |
| pass_rate     | REAL          | DEFAULT 0.0                            |

#### `audit_log`
| Column        | Type          | Constraints                            |
|---------------|---------------|----------------------------------------|
| id            | INT (PK)      | AUTO_INCREMENT                         |
| user_id       | INT (FK)      | → users(id)                            |
| action        | VARCHAR(100)  | NOT NULL                               |
| entity_type   | VARCHAR(50)   |                                        |
| entity_id     | INT           |                                        |
| old_values    | TEXT          |                                        |
| new_values    | TEXT          |                                        |
| timestamp     | TIMESTAMP     | DEFAULT CURRENT_TIMESTAMP              |

### Performance Indexes

| Index Name                              | Table              | Column(s)      |
|-----------------------------------------|--------------------|----------------|
| idx_users_username                      | users              | username       |
| idx_users_role                          | users              | role           |
| idx_test_results_user_id                | test_results       | user_id        |
| idx_test_results_test_case_id           | test_results       | test_case_id   |
| idx_test_results_start_time             | test_results       | start_time     |
| idx_test_stage_results_test_result_id   | test_stage_results | test_result_id |
| idx_test_stages_test_case_id            | test_stages        | test_case_id   |
| idx_jig_diagrams_test_case_id           | jig_diagrams       | test_case_id   |
| idx_audit_log_user_id                   | audit_log          | user_id        |
| idx_audit_log_timestamp                 | audit_log          | timestamp      |

See [`database_schema.sql`](database_schema.sql) for complete CREATE TABLE statements.

---

## User Roles & Permissions

| Feature                   | Admin | Manager | Tester |
|---------------------------|:-----:|:-------:|:------:|
| Login & Dashboard         |  ✅   |   ✅    |  ✅    |
| Run Tests                 |  ✅   |   ✅    |  ✅    |
| View Test Results         |  ✅   |   ✅    |  ✅    |
| View Jig Diagrams         |  ✅   |   ✅    |  ✅    |
| Create/Edit Test Cases    |  ✅   |   ✅    |  ❌    |
| Build Multi-Stage Tests   |  ✅   |   ✅    |  ❌    |
| Export Data               |  ✅   |   ✅    |  ❌    |
| Upload Jig Diagrams       |  ✅   |   ❌    |  ❌    |
| Configure COM Ports       |  ✅   |   ❌    |  ❌    |
| User Management           |  ✅   |   ❌    |  ❌    |

**Role Hierarchy:** Admin (Level 3) > Manager (Level 2) > Tester (Level 1)

---

## Test Parameter Ranges (Default)

| Parameter   | Minimum | Maximum | Unit |
|-------------|---------|---------|------|
| Voltage     | 4.5     | 5.5     | V    |
| Current     | 0.1     | 1.0     | A    |
| Resistance  | 90      | 110     | Ω    |

Custom thresholds can be defined per test case and per stage via the Test Case Editor and Stage Builder.

---

## Project Structure

```
PCB Testing System/
├── main.py                       # Application entry point (CustomTkinter)
├── requirements.txt              # Python dependencies
├── init_mysql.py                 # Database initialization script
├── health_checker.py             # System health diagnostics
├── api_endpoint_checker.py       # API endpoint validation (28+ tests)
├── database_schema.sql           # Full SQL schema definition
├── complete-table.sql            # Comprehensive JOIN query
│
├── config/
│   └── config.py                 # MySQL connection & app configuration
│
├── data/
│   ├── database.py               # Database class (700+ lines, 40+ methods)
│   ├── database_utils.py         # Backup, export, maintenance utilities
│   └── backups/                  # Database backup storage
│
├── ui/
│   ├── login_window.py           # Authentication screen
│   ├── dashboard.py              # Main navigation hub
│   ├── start_test.py             # Single test execution
│   ├── advanced_test.py          # Multi-stage test runner
│   ├── results_history.py        # Test result viewer with filters
│   ├── test_case_editor.py       # Test profile manager
│   ├── stage_builder.py          # Multi-stage sequence builder
│   ├── jig_diagram_viewer.py     # Jig reference image viewer
│   └── communication_config.py   # Serial port settings UI
│
├── utils/
│   └── serial_handler.py         # PySerial communication handler
│
├── assets/
│   ├── logo.png                  # Forbes Marshall logo
│   └── diagrams/                 # Jig diagram images
│
└── docs/
    ├── BARCODE_SETUP.md          # Barcode scanner configuration
    ├── DATABASE_DOCUMENTATION.md # Database reference
    ├── DATABASE_SETUP.md         # Database setup guide
    └── MYSQL_SETUP.md            # MySQL installation guide
```

---

## Serial Communication

### Data Format
PCB sends data via COM port in the format:
```
V:5.0,C:0.5,R:100.0
```
- `V` = Voltage (Volts) | `C` = Current (Amperes) | `R` = Resistance (Ohms)

### Configuration
1. Admin configures COM port settings (baud rate, data bits, stop bits, parity, timeout) via **Communication Config**
2. Test connection before saving
3. Testers toggle serial mode in Start Test / Advanced Test windows
4. System reads measured values directly from hardware when enabled

---

## Barcode Scanner Support

- Works with any USB barcode scanner in keyboard emulation mode
- Auto-focus on PCB ID field when test windows open
- Scanned data is automatically captured with visual feedback
- See [`docs/BARCODE_SETUP.md`](docs/BARCODE_SETUP.md) for detailed setup

---

## Verification & Diagnostics

```bash
# System health check (connectivity, tables, auth, CRUD, performance)
python health_checker.py

# API endpoint validation (28+ endpoints tested)
python api_endpoint_checker.py
```

Both tools generate JSON reports (`health_check_report.json`, `api_check_report.json`).

---

## Security

- **bcrypt** password hashing — no plain-text password storage
- Role-based access control at both UI and data layers
- Foreign key constraints for referential integrity
- Complete **audit logging** with old/new value tracking
- Input validation on all test parameters
- Session management with secure logout

---

## Documentation

| Document                                                   | Purpose                                |
|------------------------------------------------------------|----------------------------------------|
| [`GETTING_STARTED.md`](GETTING_STARTED.md)                 | 7-step quick start guide               |
| [`docs/MYSQL_SETUP.md`](docs/MYSQL_SETUP.md)               | Comprehensive MySQL setup & maintenance|
| [`docs/DATABASE_SETUP.md`](docs/DATABASE_SETUP.md)         | Database configuration guide           |
| [`docs/BARCODE_SETUP.md`](docs/BARCODE_SETUP.md)           | Barcode scanner setup                  |
| [`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md)         | Complete documentation index           |
| [`PPT_PROMPT.md`](PPT_PROMPT.md)                           | Detailed prompt for PPT generation     |

---

## License

This project was developed as an industry project for **Forbes Marshall**.

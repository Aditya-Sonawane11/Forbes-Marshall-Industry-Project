-- PCB Testing Automation System - SQL Database Schema
-- Database: pcb_testing

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('Admin', 'Manager', 'Tester')),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Test Cases Table
CREATE TABLE IF NOT EXISTS test_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    voltage_min REAL NOT NULL,
    voltage_max REAL NOT NULL,
    current_min REAL NOT NULL,
    current_max REAL NOT NULL,
    resistance_min REAL NOT NULL,
    resistance_max REAL NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Test Stages Table
CREATE TABLE IF NOT EXISTS test_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    stage_number INTEGER NOT NULL,
    stage_name VARCHAR(100) NOT NULL,
    description TEXT,
    voltage_min REAL,
    voltage_max REAL,
    current_min REAL,
    current_max REAL,
    resistance_min REAL,
    resistance_max REAL,
    duration_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    UNIQUE(test_case_id, stage_number)
);

-- Test Results Table
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    pcb_serial_number VARCHAR(100),
    status VARCHAR(20) NOT NULL CHECK(status IN ('Pass', 'Fail', 'In Progress')),
    overall_pass BOOLEAN,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Test Stage Results Table (for individual stage results)
CREATE TABLE IF NOT EXISTS test_stage_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_result_id INTEGER NOT NULL,
    stage_id INTEGER NOT NULL,
    voltage_measured REAL,
    current_measured REAL,
    resistance_measured REAL,
    status VARCHAR(20) NOT NULL CHECK(status IN ('Pass', 'Fail', 'Not Run')),
    failure_reason TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_result_id) REFERENCES test_results(id) ON DELETE CASCADE,
    FOREIGN KEY (stage_id) REFERENCES test_stages(id)
);

-- Communication Config Table
CREATE TABLE IF NOT EXISTS communication_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_name VARCHAR(100) NOT NULL,
    com_port VARCHAR(10),
    baud_rate INTEGER DEFAULT 9600,
    data_bits INTEGER DEFAULT 8,
    stop_bits INTEGER DEFAULT 1,
    parity VARCHAR(10) DEFAULT 'None',
    timeout_seconds INTEGER DEFAULT 5,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Jig Diagrams Table
CREATE TABLE IF NOT EXISTS jig_diagrams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER,
    diagram_name VARCHAR(100) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    description TEXT,
    uploaded_by INTEGER NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Test Statistics (Summary Table)
CREATE TABLE IF NOT EXISTS test_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_case_id INTEGER NOT NULL,
    total_tests INTEGER DEFAULT 0,
    passed_tests INTEGER DEFAULT 0,
    failed_tests INTEGER DEFAULT 0,
    pass_rate REAL DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
    UNIQUE(test_case_id)
);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_test_results_user_id ON test_results(user_id);
CREATE INDEX IF NOT EXISTS idx_test_results_test_case_id ON test_results(test_case_id);
CREATE INDEX IF NOT EXISTS idx_test_results_start_time ON test_results(start_time);
CREATE INDEX IF NOT EXISTS idx_test_stage_results_test_result_id ON test_stage_results(test_result_id);
CREATE INDEX IF NOT EXISTS idx_test_stages_test_case_id ON test_stages(test_case_id);
CREATE INDEX IF NOT EXISTS idx_jig_diagrams_test_case_id ON jig_diagrams(test_case_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

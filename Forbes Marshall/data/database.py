"""
Database Management - MySQL Implementation
SQL Database for PCB Testing Automation System
"""
import mysql.connector
from mysql.connector import Error
import bcrypt
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT, ROLE_ADMIN, ROLE_MANAGER, ROLE_TESTER
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

# Type alias for database records
DBRecord = Dict[str, Any]

class Database:
    def __init__(self) -> None:
        self.conn: Any = None
        self.cursor: Any = None
        self.init_database()
    
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                port=DB_PORT,
                autocommit=False
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def close(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def init_database(self) -> None:
        """Initialize database tables and default users"""
        try:
            # First, connect to MySQL server without database to create the database if needed
            conn_temp = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                port=DB_PORT
            )
            cursor_temp = conn_temp.cursor()
            
            # Create database if it doesn't exist
            cursor_temp.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            cursor_temp.close()
            conn_temp.close()
            
            # Now connect to the specific database
            self.connect()
            
            # Enable foreign key support
            self.cursor.execute("SET FOREIGN_KEY_CHECKS=1")
            
            # Users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('Admin', 'Manager', 'Tester') NOT NULL,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    INDEX idx_username (username),
                    INDEX idx_role (role)
                )
            ''')
            
            # Test cases table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_cases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    voltage_min DECIMAL(10, 2) NOT NULL,
                    voltage_max DECIMAL(10, 2) NOT NULL,
                    current_min DECIMAL(10, 2) NOT NULL,
                    current_max DECIMAL(10, 2) NOT NULL,
                    resistance_min DECIMAL(10, 2) NOT NULL,
                    resistance_max DECIMAL(10, 2) NOT NULL,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    INDEX idx_created_by (created_by)
                )
            ''')
            
            # Test stages table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_stages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_case_id INT NOT NULL,
                    stage_number INT NOT NULL,
                    stage_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    voltage_min DECIMAL(10, 2),
                    voltage_max DECIMAL(10, 2),
                    current_min DECIMAL(10, 2),
                    current_max DECIMAL(10, 2),
                    resistance_min DECIMAL(10, 2),
                    resistance_max DECIMAL(10, 2),
                    duration_seconds INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_stage (test_case_id, stage_number),
                    INDEX idx_test_case_id (test_case_id)
                )
            ''')
            
            # Test results table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_case_id INT NOT NULL,
                    user_id INT NOT NULL,
                    pcb_serial_number VARCHAR(255),
                    status ENUM('Pass', 'Fail', 'In Progress') NOT NULL,
                    overall_pass BOOLEAN,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    INDEX idx_user_id (user_id),
                    INDEX idx_test_case_id (test_case_id),
                    INDEX idx_start_time (start_time)
                )
            ''')
            
            # Test stage results table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_stage_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_result_id INT NOT NULL,
                    stage_id INT NOT NULL,
                    voltage_measured DECIMAL(10, 2),
                    current_measured DECIMAL(10, 2),
                    resistance_measured DECIMAL(10, 2),
                    status ENUM('Pass', 'Fail', 'Not Run') NOT NULL,
                    failure_reason TEXT,
                    start_time TIMESTAMP NULL,
                    end_time TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_result_id) REFERENCES test_results(id) ON DELETE CASCADE,
                    FOREIGN KEY (stage_id) REFERENCES test_stages(id),
                    INDEX idx_test_result_id (test_result_id)
                )
            ''')
            
            # Jig diagrams table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS jig_diagrams (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_case_id INT,
                    diagram_name VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    description TEXT,
                    uploaded_by INT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE SET NULL,
                    FOREIGN KEY (uploaded_by) REFERENCES users(id),
                    INDEX idx_test_case_id (test_case_id)
                )
            ''')
            
            # Communication configuration table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS communication_config (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    config_name VARCHAR(255) NOT NULL,
                    com_port VARCHAR(50),
                    baud_rate INT DEFAULT 9600,
                    data_bits INT DEFAULT 8,
                    stop_bits INT DEFAULT 1,
                    parity VARCHAR(10) DEFAULT 'None',
                    timeout_seconds INT DEFAULT 5,
                    created_by INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    INDEX idx_created_by (created_by)
                )
            ''')
            
            # Test statistics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_statistics (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_case_id INT NOT NULL,
                    total_tests INT DEFAULT 0,
                    passed_tests INT DEFAULT 0,
                    failed_tests INT DEFAULT 0,
                    pass_rate DECIMAL(5, 2) DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_case_id) REFERENCES test_cases(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_test_case (test_case_id),
                    INDEX idx_test_case_id (test_case_id)
                )
            ''')
            
            # Audit log table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(255) NOT NULL,
                    entity_type VARCHAR(255),
                    entity_id INT,
                    old_values JSON,
                    new_values JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    INDEX idx_user_id (user_id),
                    INDEX idx_timestamp (timestamp)
                )
            ''')
            
            self.conn.commit()
            self._create_default_users()
            
        except Error as e:
            print(f"Error initializing database: {e}")
            raise
    
    def _create_default_users(self) -> None:
        """Create default users if they don't exist"""
        default_users: List[tuple] = [
            ("admin", "admin123", ROLE_ADMIN),
            ("manager", "manager123", ROLE_MANAGER),
            ("tester", "tester123", ROLE_TESTER)
        ]
        
        for username, password, role in default_users:
            if not self.user_exists(username):
                self.create_user(username, password, role)
    
    def user_exists(self, username):
        """Check if user exists"""
        try:
            self.cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def create_user(self, username, password, role):
        """Create a new user"""
        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, password_hash, role)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[DBRecord]:
        """Authenticate user"""
        try:
            self.cursor.execute("SELECT id, password_hash, role FROM users WHERE username = %s", (username,))
            user = self.cursor.fetchone()
            
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {'id': user['id'], 'username': username, 'role': user['role']}
            return None
        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None
    
    def get_user_id(self, username: str) -> Optional[int]:
        """Get user ID by username"""
        try:
            self.cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result: Optional[DBRecord] = self.cursor.fetchone()
            return int(result['id']) if result else None
        except Exception as e:
            print(f"Error getting user ID: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[DBRecord]:
        """Get user details by ID"""
        try:
            self.cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def save_test_case(self, name, description, voltage_min, voltage_max, current_min, current_max, 
                      resistance_min, resistance_max, created_by):
        """Save a new test case"""
        try:
            self.cursor.execute(
                """INSERT INTO test_cases (name, description, voltage_min, voltage_max, current_min, 
                   current_max, resistance_min, resistance_max, created_by) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, description, voltage_min, voltage_max, current_min, current_max, 
                 resistance_min, resistance_max, created_by)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving test case: {e}")
            return None
    
    def get_test_cases(self) -> List[DBRecord]:
        """Get all test cases"""
        try:
            self.cursor.execute("SELECT * FROM test_cases ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting test cases: {e}")
            return []
    
    def get_test_case_by_id(self, test_case_id):
        """Get test case by ID"""
        try:
            self.cursor.execute("SELECT * FROM test_cases WHERE id = %s", (test_case_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting test case: {e}")
            return None
    
    def delete_test_case(self, test_case_id):
        """Delete test case (cascades to stages and results)"""
        try:
            self.cursor.execute("DELETE FROM test_cases WHERE id = %s", (test_case_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting test case: {e}")
            return False
    
    def save_test_sequence(self, sequence_name, pcb_type, stages, username):
        """Save a complete test sequence with stages"""
        try:
            # Get user ID
            user_id = self.get_user_id(username)
            if not user_id:
                print(f"Error: User '{username}' not found")
                return False
            
            # Get min/max values from all stages for test_case
            v_min = min([stage['voltage_min'] for stage in stages])
            v_max = max([stage['voltage_max'] for stage in stages])
            c_min = min([stage['current_min'] for stage in stages])
            c_max = max([stage['current_max'] for stage in stages])
            r_min = min([stage['resistance_min'] for stage in stages])
            r_max = max([stage['resistance_max'] for stage in stages])
            
            # Save test case
            test_case_id = self.save_test_case(
                name=sequence_name,
                description=pcb_type,
                voltage_min=v_min,
                voltage_max=v_max,
                current_min=c_min,
                current_max=c_max,
                resistance_min=r_min,
                resistance_max=r_max,
                created_by=user_id
            )
            
            if not test_case_id:
                return False
            
            # Save each stage
            for stage_number, stage in enumerate(stages, start=1):
                stage_name = stage.get('name', f'Stage {stage_number}')
                self.save_test_stage(
                    test_case_id=test_case_id,
                    stage_number=stage_number,
                    stage_name=stage_name,
                    description=f'Stage {stage_number}: {stage_name}',
                    voltage_min=stage['voltage_min'],
                    voltage_max=stage['voltage_max'],
                    current_min=stage['current_min'],
                    current_max=stage['current_max'],
                    resistance_min=stage['resistance_min'],
                    resistance_max=stage['resistance_max']
                )
            
            return True
        except Exception as e:
            print(f"Error saving test sequence: {e}")
            return False
    
    def save_test_stage(self, test_case_id, stage_number, stage_name, description, 
                       voltage_min, voltage_max, current_min, current_max, 
                       resistance_min, resistance_max):
        """Save a test stage"""
        try:
            self.cursor.execute(
                """INSERT INTO test_stages (test_case_id, stage_number, stage_name, description, 
                   voltage_min, voltage_max, current_min, current_max, resistance_min, resistance_max) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (test_case_id, stage_number, stage_name, description, voltage_min, voltage_max, 
                 current_min, current_max, resistance_min, resistance_max)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving test stage: {e}")
            return None
    
    def get_test_stages(self, test_case_id: int) -> List[DBRecord]:
        """Get all stages for a test case"""
        try:
            self.cursor.execute(
                "SELECT * FROM test_stages WHERE test_case_id = %s ORDER BY stage_number", 
                (test_case_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting test stages: {e}")
            return []
    
    def get_stage_by_id(self, stage_id):
        """Get stage by ID"""
        try:
            self.cursor.execute("SELECT * FROM test_stages WHERE id = %s", (stage_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting stage: {e}")
            return None
    
    def save_test_result(self, test_case_id, user_id, pcb_serial_number, status, 
                        overall_pass=None, notes=None):
        """Save a test result"""
        try:
            self.cursor.execute(
                """INSERT INTO test_results (test_case_id, user_id, pcb_serial_number, status, overall_pass, notes) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (test_case_id, user_id, pcb_serial_number, status, overall_pass, notes)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving test result: {e}")
            return None
    
    def update_test_result_status(self, result_id, status, overall_pass=None):
        """Update test result status"""
        try:
            self.cursor.execute(
                "UPDATE test_results SET status = %s, overall_pass = %s, end_time = NOW() WHERE id = %s",
                (status, overall_pass, result_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating test result: {e}")
            return False
    
    def get_test_results(self) -> List[DBRecord]:
        """Get all test results"""
        try:
            self.cursor.execute("SELECT * FROM test_results ORDER BY start_time DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting test results: {e}")
            return []
    
    def get_test_result_by_id(self, result_id):
        """Get test result by ID"""
        try:
            self.cursor.execute("SELECT * FROM test_results WHERE id = %s", (result_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting test result: {e}")
            return None
    
    def save_stage_result(self, test_result_id, stage_id, voltage_measured, current_measured, 
                         resistance_measured, status, failure_reason=None):
        """Save a stage result"""
        try:
            self.cursor.execute(
                """INSERT INTO test_stage_results (test_result_id, stage_id, voltage_measured, current_measured, 
                   resistance_measured, status, failure_reason, start_time, end_time) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (test_result_id, stage_id, voltage_measured, current_measured, resistance_measured, status, failure_reason)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving stage result: {e}")
            return None
    
    def get_stage_results(self, test_result_id):
        """Get all stage results for a test result"""
        try:
            self.cursor.execute(
                "SELECT * FROM test_stage_results WHERE test_result_id = %s ORDER BY created_at", 
                (test_result_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting stage results: {e}")
            return []
    
    def save_jig_diagram(self, test_case_id, diagram_name, file_path, description, uploaded_by):
        """Save a jig diagram"""
        try:
            self.cursor.execute(
                """INSERT INTO jig_diagrams (test_case_id, diagram_name, file_path, description, uploaded_by) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (test_case_id, diagram_name, file_path, description, uploaded_by)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving jig diagram: {e}")
            return None
    
    def get_jig_diagrams(self) -> List[DBRecord]:
        """Get all jig diagrams"""
        try:
            self.cursor.execute("SELECT * FROM jig_diagrams ORDER BY uploaded_at DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting jig diagrams: {e}")
            return []
    
    def delete_jig_diagram(self, diagram_id):
        """Delete a jig diagram"""
        try:
            self.cursor.execute("DELETE FROM jig_diagrams WHERE id = %s", (diagram_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error deleting jig diagram: {e}")
            return False
    
    def save_comm_config(self, config_name, com_port, baud_rate, data_bits, stop_bits, 
                        parity, timeout_seconds, created_by):
        """Save communication configuration"""
        try:
            self.cursor.execute(
                """INSERT INTO communication_config (config_name, com_port, baud_rate, data_bits, stop_bits, parity, timeout_seconds, created_by) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (config_name, com_port, baud_rate, data_bits, stop_bits, parity, timeout_seconds, created_by)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error saving communication config: {e}")
            return None
    
    def get_comm_config(self) -> Optional[DBRecord]:
        """Get the default communication configuration"""
        try:
            self.cursor.execute("SELECT * FROM communication_config ORDER BY created_at DESC LIMIT 1")
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting communication config: {e}")
            return None
    
    def get_all_comm_configs(self) -> List[DBRecord]:
        """Get all communication configurations"""
        try:
            self.cursor.execute("SELECT * FROM communication_config ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting communication configs: {e}")
            return []
    
    def update_test_statistics(self, test_case_id):
        """Update test statistics for a test case"""
        try:
            # Get statistics
            self.cursor.execute(
                """SELECT 
                   COUNT(*) as total, 
                   SUM(CASE WHEN overall_pass = 1 THEN 1 ELSE 0 END) as passed,
                   SUM(CASE WHEN overall_pass = 0 THEN 1 ELSE 0 END) as failed
                   FROM test_results WHERE test_case_id = %s""",
                (test_case_id,)
            )
            stats = self.cursor.fetchone()
            
            total = stats['total'] or 0
            passed = stats['passed'] or 0
            failed = stats['failed'] or 0
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            # Insert or update statistics
            self.cursor.execute(
                """INSERT INTO test_statistics (test_case_id, total_tests, passed_tests, failed_tests, pass_rate) 
                   VALUES (%s, %s, %s, %s, %s) 
                   ON DUPLICATE KEY UPDATE 
                   total_tests = %s, passed_tests = %s, failed_tests = %s, pass_rate = %s""",
                (test_case_id, total, passed, failed, pass_rate, total, passed, failed, pass_rate)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating test statistics: {e}")
            return False
    
    def get_test_statistics(self, test_case_id):
        """Get test statistics for a test case"""
        try:
            self.cursor.execute(
                "SELECT * FROM test_statistics WHERE test_case_id = %s", 
                (test_case_id,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting test statistics: {e}")
            return None
    
    def log_action(self, user_id, action, entity_type=None, entity_id=None, 
                  old_values=None, new_values=None):
        """Log user action in audit log"""
        try:
            old_values_json = json.dumps(old_values) if old_values else None
            new_values_json = json.dumps(new_values) if new_values else None
            
            self.cursor.execute(
                """INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, new_values) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, action, entity_type, entity_id, old_values_json, new_values_json)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.conn.rollback()
            print(f"Error logging action: {e}")
            return None
    
    def get_audit_log(self) -> List[DBRecord]:
        """Get audit log entries"""
        try:
            self.cursor.execute("SELECT * FROM audit_log ORDER BY timestamp DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting audit log: {e}")
            return []
    
    def export_test_results_to_csv(self, test_case_id=None):
        """Export test results to CSV"""
        try:
            import csv
            from datetime import datetime
            
            if test_case_id:
                self.cursor.execute(
                    "SELECT * FROM test_results WHERE test_case_id = %s ORDER BY start_time DESC",
                    (test_case_id,)
                )
            else:
                self.cursor.execute("SELECT * FROM test_results ORDER BY start_time DESC")
            
            results = self.cursor.fetchall()
            filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            if results:
                with open(filename, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    for row in results:
                        writer.writerow(row)
            
            return filename
        except Exception as e:
            print(f"Error exporting results: {e}")
            return None

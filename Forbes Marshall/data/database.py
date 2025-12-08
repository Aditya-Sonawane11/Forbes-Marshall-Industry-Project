"""
Database Management
"""
import sqlite3
import bcrypt
from config.config import DB_PATH, ROLE_ADMIN, ROLE_MANAGER, ROLE_TESTER

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """Initialize database tables and default users"""
        self.connect()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test results table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_id TEXT NOT NULL,
                tester_username TEXT NOT NULL,
                test_status TEXT NOT NULL,
                voltage REAL,
                current REAL,
                resistance REAL,
                notes TEXT,
                tested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test cases table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pcb_type TEXT NOT NULL,
                voltage_min REAL NOT NULL,
                voltage_max REAL NOT NULL,
                current_min REAL NOT NULL,
                current_max REAL NOT NULL,
                resistance_min REAL NOT NULL,
                resistance_max REAL NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test sequences table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS test_sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_name TEXT NOT NULL,
                pcb_type TEXT NOT NULL,
                total_stages INTEGER NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test sequence stages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sequence_stages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_id INTEGER NOT NULL,
                stage_name TEXT NOT NULL,
                voltage_min REAL NOT NULL,
                voltage_max REAL NOT NULL,
                current_min REAL NOT NULL,
                current_max REAL NOT NULL,
                resistance_min REAL NOT NULL,
                resistance_max REAL NOT NULL,
                stage_order INTEGER NOT NULL,
                FOREIGN KEY (sequence_id) REFERENCES test_sequences(id) ON DELETE CASCADE
            )
        ''')
        
        # Jig diagrams table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS jig_diagrams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                pcb_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                description TEXT,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Communication configuration table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS comm_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                port TEXT NOT NULL,
                baud_rate INTEGER NOT NULL,
                data_bits INTEGER NOT NULL,
                parity TEXT NOT NULL,
                stop_bits TEXT NOT NULL,
                timeout REAL NOT NULL,
                updated_by TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
        self._create_default_users()
        self.close()
    
    def _create_default_users(self):
        """Create default users if they don't exist"""
        default_users = [
            ("admin", "admin123", ROLE_ADMIN),
            ("manager", "manager123", ROLE_MANAGER),
            ("tester", "tester123", ROLE_TESTER)
        ]
        
        for username, password, role in default_users:
            if not self.user_exists(username):
                self.create_user(username, password, role)
    
    def user_exists(self, username):
        """Check if user exists"""
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return self.cursor.fetchone() is not None
    
    def create_user(self, username, password, role):
        """Create a new user"""
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, password_hash, role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username, password):
        """Authenticate user and return role if successful"""
        self.connect()
        self.cursor.execute(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        result = self.cursor.fetchone()
        self.close()
        
        if result:
            password_hash, role = result
            if bcrypt.checkpw(password.encode('utf-8'), password_hash):
                return role
        return None
    
    def save_test_result(self, pcb_id, tester_username, test_status, voltage, current, resistance, notes=""):
        """Save test result to database"""
        self.connect()
        self.cursor.execute('''
            INSERT INTO test_results 
            (pcb_id, tester_username, test_status, voltage, current, resistance, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (pcb_id, tester_username, test_status, voltage, current, resistance, notes))
        self.conn.commit()
        self.close()
    
    def get_test_results(self, username=None):
        """Get test results, optionally filtered by username"""
        self.connect()
        if username:
            self.cursor.execute('''
                SELECT id, pcb_id, tester_username, test_status, voltage, current, resistance, notes, 
                       datetime(tested_at, 'localtime') as tested_at
                FROM test_results 
                WHERE tester_username = ?
                ORDER BY tested_at DESC
            ''', (username,))
        else:
            self.cursor.execute('''
                SELECT id, pcb_id, tester_username, test_status, voltage, current, resistance, notes,
                       datetime(tested_at, 'localtime') as tested_at
                FROM test_results 
                ORDER BY tested_at DESC
            ''')
        results = self.cursor.fetchall()
        self.close()
        return results
    
    def save_test_case(self, pcb_type, voltage_min, voltage_max, current_min, current_max, 
                       resistance_min, resistance_max, description, created_by):
        """Save test case to database"""
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO test_cases 
                (pcb_type, voltage_min, voltage_max, current_min, current_max, 
                 resistance_min, resistance_max, description, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pcb_type, voltage_min, voltage_max, current_min, current_max,
                  resistance_min, resistance_max, description, created_by))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Error saving test case: {e}")
            self.close()
            return False
    
    def get_test_cases(self):
        """Get all test cases"""
        self.connect()
        self.cursor.execute('''
            SELECT id, pcb_type, voltage_min, voltage_max, current_min, current_max,
                   resistance_min, resistance_max, description, created_by,
                   datetime(created_at, 'localtime') as created_at
            FROM test_cases 
            ORDER BY created_at DESC
        ''')
        results = self.cursor.fetchall()
        self.close()
        return results
    
    def delete_test_case(self, tc_id):
        """Delete a test case"""
        self.connect()
        self.cursor.execute('DELETE FROM test_cases WHERE id = ?', (tc_id,))
        self.conn.commit()
        self.close()
    
    def save_test_sequence(self, sequence_name, pcb_type, stages, created_by):
        """Save test sequence with stages"""
        self.connect()
        try:
            # Save sequence
            self.cursor.execute('''
                INSERT INTO test_sequences 
                (sequence_name, pcb_type, total_stages, created_by)
                VALUES (?, ?, ?, ?)
            ''', (sequence_name, pcb_type, len(stages), created_by))
            
            sequence_id = self.cursor.lastrowid
            
            # Save stages
            for idx, stage in enumerate(stages):
                self.cursor.execute('''
                    INSERT INTO sequence_stages 
                    (sequence_id, stage_name, voltage_min, voltage_max, current_min, current_max,
                     resistance_min, resistance_max, stage_order)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sequence_id, stage['name'], stage['voltage_min'], stage['voltage_max'],
                      stage['current_min'], stage['current_max'], stage['resistance_min'],
                      stage['resistance_max'], idx + 1))
            
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Error saving test sequence: {e}")
            self.close()
            return False
    
    def get_test_sequences(self):
        """Get all test sequences"""
        self.connect()
        self.cursor.execute('''
            SELECT id, sequence_name, pcb_type, total_stages, created_by,
                   datetime(created_at, 'localtime') as created_at
            FROM test_sequences 
            ORDER BY created_at DESC
        ''')
        results = self.cursor.fetchall()
        self.close()
        return results
    
    def get_sequence_stages(self, sequence_id):
        """Get stages for a specific sequence"""
        self.connect()
        self.cursor.execute('''
            SELECT id, sequence_id, stage_name, voltage_min, voltage_max, current_min, current_max,
                   resistance_min, resistance_max, stage_order
            FROM sequence_stages 
            WHERE sequence_id = ?
            ORDER BY stage_order
        ''', (sequence_id,))
        results = self.cursor.fetchall()
        self.close()
        return results
    
    def delete_test_sequence(self, seq_id):
        """Delete a test sequence and its stages"""
        self.connect()
        self.cursor.execute('DELETE FROM sequence_stages WHERE sequence_id = ?', (seq_id,))
        self.cursor.execute('DELETE FROM test_sequences WHERE id = ?', (seq_id,))
        self.conn.commit()
        self.close()
    
    def save_jig_diagram(self, name, pcb_type, file_path, description, uploaded_by):
        """Save jig diagram information"""
        self.connect()
        try:
            self.cursor.execute('''
                INSERT INTO jig_diagrams 
                (name, pcb_type, file_path, description, uploaded_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, pcb_type, file_path, description, uploaded_by))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Error saving jig diagram: {e}")
            self.close()
            return False
    
    def get_jig_diagrams(self):
        """Get all jig diagrams"""
        self.connect()
        self.cursor.execute('''
            SELECT id, name, pcb_type, file_path, description, uploaded_by,
                   datetime(uploaded_at, 'localtime') as uploaded_at
            FROM jig_diagrams 
            ORDER BY uploaded_at DESC
        ''')
        results = self.cursor.fetchall()
        self.close()
        return results
    
    def delete_jig_diagram(self, diagram_id):
        """Delete a jig diagram"""
        self.connect()
        self.cursor.execute('DELETE FROM jig_diagrams WHERE id = ?', (diagram_id,))
        self.conn.commit()
        self.close()
    
    def save_comm_config(self, config, updated_by):
        """Save communication configuration"""
        self.connect()
        try:
            # Check if config exists
            self.cursor.execute('SELECT id FROM comm_config LIMIT 1')
            exists = self.cursor.fetchone()
            
            if exists:
                # Update existing
                self.cursor.execute('''
                    UPDATE comm_config 
                    SET port = ?, baud_rate = ?, data_bits = ?, parity = ?, 
                        stop_bits = ?, timeout = ?, updated_by = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (config['port'], config['baud_rate'], config['data_bits'], 
                      config['parity'], config['stop_bits'], config['timeout'], 
                      updated_by, exists[0]))
            else:
                # Insert new
                self.cursor.execute('''
                    INSERT INTO comm_config 
                    (port, baud_rate, data_bits, parity, stop_bits, timeout, updated_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (config['port'], config['baud_rate'], config['data_bits'],
                      config['parity'], config['stop_bits'], config['timeout'], updated_by))
            
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            print(f"Error saving comm config: {e}")
            self.close()
            return False
    
    def get_comm_config(self):
        """Get communication configuration"""
        self.connect()
        self.cursor.execute('''
            SELECT port, baud_rate, data_bits, parity, stop_bits, timeout
            FROM comm_config 
            ORDER BY updated_at DESC
            LIMIT 1
        ''')
        result = self.cursor.fetchone()
        self.close()
        
        if result:
            return {
                'port': result[0],
                'baud_rate': result[1],
                'data_bits': result[2],
                'parity': result[3],
                'stop_bits': result[4],
                'timeout': result[5]
            }
        return None

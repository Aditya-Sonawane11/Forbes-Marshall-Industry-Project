"""
Database Utilities - MySQL Implementation
Backup, maintenance, and data management utilities for PCB Testing system
"""
import mysql.connector
from mysql.connector import Error
import os
import csv
import json
import subprocess
from datetime import datetime
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT

class DatabaseUtilities:
    """Utilities for database maintenance and backup"""
    
    def __init__(self):
        self.db_host = DB_HOST
        self.db_user = DB_USER
        self.db_password = DB_PASSWORD
        self.db_name = DB_NAME
        self.db_port = DB_PORT
        self.backup_dir = 'data/backups'
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def connect(self):
        """Create database connection"""
        try:
            return mysql.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                port=self.db_port
            )
        except Error as e:
            print(f"Connection error: {e}")
            return None
    
    # ============== BACKUP OPERATIONS ==============
    
    def create_backup(self, backup_name=None):
        """
        Create a backup of the database using mysqldump
        
        Args:
            backup_name (str): Custom backup name, defaults to timestamp
            
        Returns:
            str: Path to backup file
        """
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'pcb_testing_backup_{timestamp}.sql'
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Construct mysqldump command
            cmd = [
                'mysqldump',
                f'-h{self.db_host}',
                f'-u{self.db_user}',
                f'-p{self.db_password}',
                f'-P{self.db_port}',
                '--routines',
                '--triggers',
                self.db_name
            ]
            
            with open(backup_path, 'w') as f:
                process = subprocess.Popen(cmd, stdout=f, stderr=subprocess.PIPE)
                _, stderr = process.communicate()
                
                if process.returncode == 0:
                    print(f"✓ Backup created: {backup_path}")
                    return backup_path
                else:
                    print(f"Backup error: {stderr.decode()}")
                    return None
                    
        except FileNotFoundError:
            print("mysqldump not found. Ensure MySQL is installed and in system PATH.")
            return None
        except Exception as e:
            print(f"Backup error: {e}")
            return None
    
    def restore_backup(self, backup_file):
        """
        Restore database from backup file
        
        Args:
            backup_file (str): Path to backup file
            
        Returns:
            bool: Success status
        """
        if not os.path.exists(backup_file):
            print(f"Backup file not found: {backup_file}")
            return False
        
        try:
            cmd = [
                'mysql',
                f'-h{self.db_host}',
                f'-u{self.db_user}',
                f'-p{self.db_password}',
                f'-P{self.db_port}',
                self.db_name
            ]
            
            with open(backup_file, 'r') as f:
                process = subprocess.Popen(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _, stderr = process.communicate()
                
                if process.returncode == 0:
                    print(f"✓ Database restored from: {backup_file}")
                    return True
                else:
                    print(f"Restore error: {stderr.decode()}")
                    return False
                    
        except FileNotFoundError:
            print("mysql not found. Ensure MySQL is installed and in system PATH.")
            return False
        except Exception as e:
            print(f"Restore error: {e}")
            return False
    
    def list_backups(self):
        """List all available backups"""
        try:
            backups = [f for f in os.listdir(self.backup_dir) if f.endswith('.sql')]
            return sorted(backups, reverse=True)
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
    
    # ============== MAINTENANCE OPERATIONS ==============
    
    def check_integrity(self):
        """Check database integrity"""
        try:
            conn = self.connect()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Check all tables
            cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{self.db_name}'")
            table_count = cursor.fetchone()[0]
            
            # Check for any errors
            cursor.execute(f"CHECK TABLE users, test_cases, test_results, test_stages, test_stage_results, jig_diagrams, communication_config, test_statistics, audit_log")
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            all_ok = all(row[3] == 'OK' for row in results if len(row) > 3)
            return all_ok and table_count > 0
            
        except Exception as e:
            print(f"Integrity check error: {e}")
            return False
    
    def vacuum_database(self):
        """Optimize database tables"""
        try:
            conn = self.connect()
            if not conn:
                return False
            
            cursor = conn.cursor()
            tables = ['users', 'test_cases', 'test_results', 'test_stages', 'test_stage_results', 
                     'jig_diagrams', 'communication_config', 'test_statistics', 'audit_log']
            
            for table in tables:
                cursor.execute(f"OPTIMIZE TABLE {table}")
                print(f"  Optimized {table}")
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Vacuum error: {e}")
            return False
    
    def get_database_stats(self):
        """Get database statistics"""
        try:
            conn = self.connect()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            stats = {}
            
            # Get table sizes
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size_MB'
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = '{self.db_name}'
                ORDER BY (data_length + index_length) DESC
            """)
            
            tables = cursor.fetchall()
            total_size = 0
            stats['tables'] = {}
            
            for table in tables:
                size = table['Size_MB'] or 0
                stats['tables'][table['TABLE_NAME']] = size
                total_size += size
            
            stats['total_size_mb'] = round(total_size, 2)
            
            # Get row counts
            cursor.execute(f"""
                SELECT 
                    TABLE_NAME,
                    TABLE_ROWS
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = '{self.db_name}'
            """)
            
            stats['row_counts'] = {row['TABLE_NAME']: row['TABLE_ROWS'] or 0 for row in cursor.fetchall()}
            
            cursor.close()
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    # ============== DATA EXPORT OPERATIONS ==============
    
    def export_table_to_csv(self, table_name, output_file=None):
        """Export table to CSV"""
        try:
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join('data', f'{table_name}_{timestamp}.csv')
            
            conn = self.connect()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row)
            
            cursor.close()
            conn.close()
            return output_file
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
    
    def export_test_results_detailed(self, output_file=None):
        """Export detailed test results"""
        try:
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join('data', f'test_results_detailed_{timestamp}.csv')
            
            conn = self.connect()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    tr.id as result_id,
                    tc.name as test_case_name,
                    u.username,
                    tr.pcb_serial_number,
                    tr.status,
                    tr.overall_pass,
                    tr.start_time,
                    tr.end_time,
                    tr.notes,
                    tsr.stage_id,
                    ts.stage_name,
                    tsr.voltage_measured,
                    tsr.current_measured,
                    tsr.resistance_measured,
                    tsr.status as stage_status
                FROM test_results tr
                JOIN test_cases tc ON tr.test_case_id = tc.id
                JOIN users u ON tr.user_id = u.id
                LEFT JOIN test_stage_results tsr ON tr.id = tsr.test_result_id
                LEFT JOIN test_stages ts ON tsr.stage_id = ts.id
                ORDER BY tr.start_time DESC
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if rows:
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(row)
            
            cursor.close()
            conn.close()
            print(f"✓ Exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
    
    # ============== DATA CLEANUP OPERATIONS ==============
    
    def delete_old_test_results(self, days=90):
        """Delete test results older than specified days"""
        try:
            conn = self.connect()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM test_results WHERE created_at < DATE_SUB(NOW(), INTERVAL {days} DAY)"
            )
            rows_deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Deleted {rows_deleted} test results older than {days} days")
            return True
            
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False
    
    def delete_old_audit_logs(self, days=180):
        """Delete audit logs older than specified days"""
        try:
            conn = self.connect()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL {days} DAY)"
            )
            rows_deleted = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Deleted {rows_deleted} audit logs older than {days} days")
            return True
            
        except Exception as e:
            print(f"Cleanup error: {e}")
            return False
    
    # ============== REPORTING OPERATIONS ==============
    
    def generate_summary_report(self):
        """Generate summary report"""
        try:
            conn = self.connect()
            if not conn:
                return None
            
            cursor = conn.cursor(dictionary=True)
            report = {}
            
            # Overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT tc.id) as total_test_cases,
                    COUNT(DISTINCT tr.id) as total_test_runs,
                    SUM(CASE WHEN tr.overall_pass = 1 THEN 1 ELSE 0 END) as passed_tests,
                    SUM(CASE WHEN tr.overall_pass = 0 THEN 1 ELSE 0 END) as failed_tests,
                    ROUND(SUM(CASE WHEN tr.overall_pass = 1 THEN 1 ELSE 0 END) / COUNT(DISTINCT tr.id) * 100, 2) as pass_rate
                FROM test_cases tc
                LEFT JOIN test_results tr ON tc.id = tr.test_case_id
            """)
            
            result = cursor.fetchone()
            report['overall'] = {
                'test_cases': result['total_test_cases'] or 0,
                'test_runs': result['total_test_runs'] or 0,
                'passed': result['passed_tests'] or 0,
                'failed': result['failed_tests'] or 0,
                'pass_rate': result['pass_rate'] or 0
            }
            
            # User activity
            cursor.execute("""
                SELECT u.username, COUNT(tr.id) as test_count
                FROM users u
                LEFT JOIN test_results tr ON u.id = tr.user_id
                GROUP BY u.id
                ORDER BY test_count DESC
            """)
            
            report['user_activity'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            return report
            
        except Exception as e:
            print(f"Report generation error: {e}")
            return None
    
    def export_report_to_json(self, output_file=None):
        """Export comprehensive report to JSON"""
        try:
            report = self.generate_summary_report()
            if not report:
                return None
            
            if output_file is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_file = os.path.join('data', f'report_{timestamp}.json')
            
            report['timestamp'] = datetime.now().isoformat()
            report['database_stats'] = self.get_database_stats()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"✓ Report exported to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Export error: {e}")
            return None

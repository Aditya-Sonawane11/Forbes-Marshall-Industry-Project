"""
API Endpoint Checker
Validates all database API endpoints and methods
"""
import sys
from datetime import datetime
from data.database import Database

class APIChecker:
    """Check all database API endpoints"""
    
    def __init__(self):
        self.db = Database()
        self.results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'endpoints': {},
            'total_endpoints': 0,
            'working_endpoints': 0,
            'failed_endpoints': 0
        }
    
    def check_endpoint(self, endpoint_name, test_func):
        """Test a single endpoint"""
        try:
            result = test_func()
            status = "✓"
            print(f"  {status} {endpoint_name:45} - OK")
            self.results['endpoints'][endpoint_name] = 'OK'
            self.results['working_endpoints'] += 1
            return True
        except Exception as e:
            status = "✗"
            error_msg = str(e)[:50]
            print(f"  {status} {endpoint_name:45} - ERROR: {error_msg}")
            self.results['endpoints'][endpoint_name] = f'ERROR - {str(e)}'
            self.results['failed_endpoints'] += 1
            return False
    
    def check_user_endpoints(self):
        """Check user management endpoints"""
        print("\n[USER MANAGEMENT ENDPOINTS]")
        
        endpoints = [
            ("authenticate_user", lambda: self.db.authenticate_user('admin', 'admin123')),
            ("create_user", lambda: self.db.create_user('test_user', 'password', 'Tester')),
            ("user_exists", lambda: self.db.user_exists('admin')),
            ("get_user_id", lambda: self.db.get_user_id('admin')),
            ("get_user_by_id", lambda: self.db.get_user_by_id(1)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"users.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_test_case_endpoints(self):
        """Check test case endpoints"""
        print("\n[TEST CASE ENDPOINTS]")
        
        user_id = self.db.get_user_id('admin')
        
        endpoints = [
            ("save_test_case", lambda: self.db.save_test_case(
                "API Test", "Test case", 4.5, 5.5, 0.1, 1.0, 90, 110, user_id
            )),
            ("get_test_cases", lambda: self.db.get_test_cases()),
            ("get_test_case_by_id", lambda: self.db.get_test_case_by_id(1)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"test_cases.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_test_stage_endpoints(self):
        """Check test stage endpoints"""
        print("\n[TEST STAGE ENDPOINTS]")
        
        test_cases = self.db.get_test_cases()
        test_case_id = test_cases[0]['id'] if test_cases else None
        
        if not test_case_id:
            print("  ⊘ Skipped (No test cases available)")
            return
        
        endpoints = [
            ("save_test_stage", lambda: self.db.save_test_stage(
                test_case_id, 1, "API Stage", None, 4.5, 5.5, 0.1, 1.0, 90, 110
            )),
            ("get_test_stages", lambda: self.db.get_test_stages(test_case_id)),
            ("get_stage_by_id", lambda: self.db.get_stage_by_id(1)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"test_stages.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_test_result_endpoints(self):
        """Check test result endpoints"""
        print("\n[TEST RESULT ENDPOINTS]")
        
        test_cases = self.db.get_test_cases()
        test_case_id = test_cases[0]['id'] if test_cases else None
        user_id = self.db.get_user_id('tester')
        
        if not test_case_id:
            print("  ⊘ Skipped (No test cases available)")
            return
        
        endpoints = [
            ("save_test_result", lambda: self.db.save_test_result(
                test_case_id, user_id, "API-TEST-001", "In Progress"
            )),
            ("update_test_result_status", lambda: self.db.update_test_result_status(1, "Pass", True)),
            ("get_test_results", lambda: self.db.get_test_results()),
            ("get_test_result_by_id", lambda: self.db.get_test_result_by_id(1)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"test_results.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_stage_result_endpoints(self):
        """Check stage result endpoints"""
        print("\n[STAGE RESULT ENDPOINTS]")
        
        results = self.db.get_test_results()
        result_id = results[0]['id'] if results else None
        
        stages = self.db.get_test_stages(1) if self.db.get_test_cases() else []
        stage_id = stages[0]['id'] if stages else None
        
        if not result_id or not stage_id:
            print("  ⊘ Skipped (No test results or stages available)")
            return
        
        endpoints = [
            ("save_stage_result", lambda: self.db.save_stage_result(
                result_id, stage_id, 5.0, 0.5, 100, "Pass"
            )),
            ("get_stage_results", lambda: self.db.get_stage_results(result_id)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"stage_results.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_jig_diagram_endpoints(self):
        """Check jig diagram endpoints"""
        print("\n[JIG DIAGRAM ENDPOINTS]")
        
        user_id = self.db.get_user_id('admin')
        
        endpoints = [
            ("save_jig_diagram", lambda: self.db.save_jig_diagram(
                None, "API Diagram", "assets/diagrams/test.png", "Test diagram", user_id
            )),
            ("get_jig_diagrams", lambda: self.db.get_jig_diagrams()),
            ("delete_jig_diagram", lambda: self.db.delete_jig_diagram(1)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"jig_diagrams.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_communication_endpoints(self):
        """Check communication config endpoints"""
        print("\n[COMMUNICATION CONFIG ENDPOINTS]")
        
        user_id = self.db.get_user_id('admin')
        
        endpoints = [
            ("save_comm_config", lambda: self.db.save_comm_config(
                "Test Config", "COM1", 9600, 8, 1, "None", 5, user_id
            )),
            ("get_comm_config", lambda: self.db.get_comm_config()),
            ("get_all_comm_configs", lambda: self.db.get_all_comm_configs()),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"communication.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_statistics_endpoints(self):
        """Check statistics endpoints"""
        print("\n[STATISTICS ENDPOINTS]")
        
        test_cases = self.db.get_test_cases()
        test_case_id = test_cases[0]['id'] if test_cases else None
        
        if not test_case_id:
            print("  ⊘ Skipped (No test cases available)")
            return
        
        endpoints = [
            ("update_test_statistics", lambda: self.db.update_test_statistics(test_case_id)),
            ("get_test_statistics", lambda: self.db.get_test_statistics(test_case_id)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"statistics.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_audit_endpoints(self):
        """Check audit logging endpoints"""
        print("\n[AUDIT LOG ENDPOINTS]")
        
        user_id = self.db.get_user_id('admin')
        
        endpoints = [
            ("log_action", lambda: self.db.log_action(user_id, "API Check", "test", 1)),
            ("get_audit_log", lambda: self.db.get_audit_log()),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"audit.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def check_export_endpoints(self):
        """Check export endpoints"""
        print("\n[EXPORT ENDPOINTS]")
        
        test_cases = self.db.get_test_cases()
        test_case_id = test_cases[0]['id'] if test_cases else None
        
        endpoints = [
            ("export_test_results_to_csv", lambda: self.db.export_test_results_to_csv(test_case_id)),
        ]
        
        for endpoint, test_func in endpoints:
            self.check_endpoint(f"export.{endpoint}", test_func)
            self.results['total_endpoints'] += 1
    
    def generate_summary(self):
        """Generate API check summary"""
        print("\n" + "="*70)
        print("API ENDPOINT CHECK SUMMARY")
        print("="*70)
        
        success_rate = (self.results['working_endpoints'] / self.results['total_endpoints'] * 100 
                       if self.results['total_endpoints'] > 0 else 0)
        
        status = "✓ ALL ENDPOINTS WORKING" if self.results['failed_endpoints'] == 0 else "⚠ SOME ENDPOINTS FAILED"
        
        print(f"\nStatus: {status}")
        print(f"Total Endpoints: {self.results['total_endpoints']}")
        print(f"Working: {self.results['working_endpoints']} ({success_rate:.1f}%)")
        print(f"Failed: {self.results['failed_endpoints']}")
        print(f"Timestamp: {self.results['timestamp']}")
        print("="*70)
    
    def export_results(self, filename="api_check_report.json"):
        """Export results to JSON"""
        import json
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n✓ Report exported to: {filename}")
            return True
        except Exception as e:
            print(f"✗ Failed to export report: {str(e)}")
            return False
    
    def run_all_checks(self, export=True):
        """Run all API endpoint checks"""
        print("\n" + "="*70)
        print("PCB TESTING SYSTEM - API ENDPOINT CHECKER")
        print("="*70)
        
        self.check_user_endpoints()
        self.check_test_case_endpoints()
        self.check_test_stage_endpoints()
        self.check_test_result_endpoints()
        self.check_stage_result_endpoints()
        self.check_jig_diagram_endpoints()
        self.check_communication_endpoints()
        self.check_statistics_endpoints()
        self.check_audit_endpoints()
        self.check_export_endpoints()
        
        self.generate_summary()
        
        if export:
            self.export_results()
        
        return self.results


def main():
    """Main entry point"""
    print("\nStarting PCB Testing System API Endpoint Check...\n")
    
    checker = APIChecker()
    results = checker.run_all_checks(export=True)
    
    # Return exit code based on results
    if results['failed_endpoints'] == 0:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
MySQL Database Initialization Script
Sets up the MySQL database with all tables and default users
"""

import sys
from data.database import Database
from config.config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def main():
    print("\n" + "="*70)
    print("PCB TESTING SYSTEM - MySQL Database Initialization")
    print("="*70)
    
    print(f"\nDatabase Configuration:")
    print(f"  Host:     {DB_HOST}")
    print(f"  User:     {DB_USER}")
    print(f"  Database: {DB_NAME}")
    print(f"  Port:     3306")
    
    try:
        print("\n[1/3] Connecting to MySQL...")
        db = Database()
        print("  ✓ Connected successfully")
        
        print("\n[2/3] Creating database tables...")
        # Database initialization happens in __init__
        print("  ✓ All tables created (or already exist)")
        
        print("\n[3/3] Verifying default users...")
        users = [
            ("admin", "Admin"),
            ("manager", "Manager"),
            ("tester", "Tester")
        ]
        
        for username, role in users:
            user_id = db.get_user_id(username)
            status = "✓" if user_id else "✗"
            print(f"  {status} {username:15} ({role:10}) - ID: {user_id}")
        
        db.close()
        
        print("\n" + "="*70)
        print("Database initialization completed successfully!")
        print("="*70)
        print("\nDefault Users:")
        print("  Username: admin     | Password: admin123  | Role: Admin")
        print("  Username: manager   | Password: manager123| Role: Manager")
        print("  Username: tester    | Password: tester123 | Role: Tester")
        print("\n⚠️  WARNING: Change these passwords immediately in production!")
        print("\nYou can now run: python main.py")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Verify MySQL server is running")
        print("  2. Check credentials in config/config.py")
        print("  3. Ensure database 'pcb_testing' can be created")
        print("\nFor detailed help, see docs/MYSQL_SETUP.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())

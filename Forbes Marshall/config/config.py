"""
Application Configuration
"""

# Window Settings
WINDOW_TITLE = "PCB Testing System - Forbes Marshall"
LOGIN_WINDOW_SIZE = "400x500"
DASHBOARD_WINDOW_SIZE = "1200x700"

# Roles
ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_TESTER = "Tester"

# Role Hierarchy (higher number = more access)
ROLE_LEVELS = {
    ROLE_ADMIN: 3,
    ROLE_MANAGER: 2,
    ROLE_TESTER: 1
}

# MySQL Database Configuration
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "pcb_testing"
DB_PORT = 3306

# Assets
LOGO_PATH = "assets/logo.png"

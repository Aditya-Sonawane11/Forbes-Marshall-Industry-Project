"""
Application Configuration
"""

# Window Settings
WINDOW_TITLE = "PCB Testing System - Forbes Marshall"
LOGIN_WINDOW_SIZE = "400x500"
DASHBOARD_WINDOW_SIZE = "1200x700"

# Roles
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_TESTER = "tester"

# Role Hierarchy (higher number = more access)
ROLE_LEVELS = {
    ROLE_ADMIN: 3,
    ROLE_MANAGER: 2,
    ROLE_TESTER: 1
}

# Database
DB_PATH = "data/pcb_testing.db"

# Assets
LOGO_PATH = "assets/logo.png"

"""
Application Configuration
"""

import os
import sys


def resource_path(relative_path: str) -> str:
    """Resolve resource paths for both development and PyInstaller bundles."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Window Settings
WINDOW_TITLE = "PCB Testing System - Forbes Marshall"
LOGIN_WINDOW_SIZE = "400x500"
DASHBOARD_WINDOW_SIZE = "1200x700"

# Roles
ROLE_ADMIN = "Admin"
ROLE_MANAGER = "Manager"
ROLE_TESTER = "Tester"

# Test Status Constants (match database ENUM values)
STATUS_PASS = "Pass"
STATUS_FAIL = "Fail"
STATUS_IN_PROGRESS = "In Progress"

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
LOGO_PATH = resource_path("assets/logo.png")

# PCB Testing Automation System - Complete

## Overview
Automated PCB testing system with role-based access control, multi-stage testing, serial communication, and comprehensive test result tracking.

## Features

### Phase 1 - Core Testing
- User authentication with role-based access (Admin, Manager, Tester)
- Dashboard with role-specific menu options
- Start Test functionality with pass/fail logic
- Test parameter validation (Voltage, Current, Resistance)
- SQLite database for user and test result storage

### Phase 2 - Test Management
- Results History with filtering and search
- Export test results to CSV
- Test Case Editor for creating custom test profiles
- Statistics and pass rate tracking
- Role-based result visibility

### Phase 3 - Advanced Testing
- Stage Builder for multi-stage test sequences
- Advanced Test runner with sequential stage execution
- Real-time stage progress tracking
- Detailed failure reporting per stage
- Custom test workflows for different PCB types

### Phase 4 - Hardware Integration
- Serial Communication (COM Port) configuration
- Real-time data reading from PCB via serial
- Jig Diagram Viewer for visual test point reference
- Admin-controlled communication settings
- Automatic/Manual test mode switching

## Installation

1. Install Python 3.8 or higher

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place the Forbes Marshall logo as `assets/logo.png`

4. Run the application:
```bash
python main.py
```

## Default Credentials
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Tester: `tester` / `tester123`

## Test Parameter Ranges
- Voltage: 4.5 - 5.5V
- Current: 0.1 - 1.0A
- Resistance: 90 - 110Ω

## Project Structure
```
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── assets/
│   ├── logo.png                # Company logo
│   └── diagrams/               # Jig diagram images
├── config/
│   └── config.py               # Configuration settings
├── data/
│   ├── database.py             # Database operations
│   └── pcb_testing.db          # SQLite database (auto-created)
├── ui/
│   ├── login_window.py         # Login screen
│   ├── dashboard.py            # Main dashboard
│   ├── start_test.py           # Basic test execution
│   ├── advanced_test.py        # Multi-stage test execution
│   ├── results_history.py      # Test results viewer
│   ├── test_case_editor.py     # Test case management
│   ├── stage_builder.py        # Multi-stage sequence builder
│   ├── jig_diagram_viewer.py   # Jig diagram viewer
│   └── communication_config.py # Serial port configuration
└── utils/
    └── serial_handler.py       # Serial communication handler
```

## Serial Communication

The system supports reading test data directly from PCBs via COM ports.

### Expected Data Format
PCB should send data in format: `V:5.0,C:0.5,R:100.0`
- V = Voltage in Volts
- C = Current in Amperes  
- R = Resistance in Ohms

### Configuration
1. Admin users configure COM port settings in "Communication Config"
2. Test connection before saving
3. Testers can toggle serial mode in "Start Test" window
4. When enabled, system reads values directly from PCB

## Jig Diagrams

Upload and view test jig diagrams for reference during testing.

### Supported Formats
- PNG, JPG, JPEG, GIF, BMP

### Usage
1. Admin uploads diagrams via "Jig Diagram Viewer"
2. All users can view diagrams organized by PCB type
3. Helps operators position PCBs correctly on test fixtures

## Barcode Scanner Support

The system supports automatic PCB ID capture via barcode scanners.

### Features
- Auto-focus on PCB ID field when test windows open
- Automatic capture of scanned barcode data
- Visual feedback for scan confirmation
- Works with any USB barcode scanner (keyboard emulation mode)

### Setup
1. Connect USB barcode scanner to computer
2. Configure scanner to send "Enter" key after each scan (most scanners do this by default)
3. Open Start Test or Advanced Test window
4. Scan PCB barcode - ID is automatically captured
5. Press Enter or click Run Test to proceed

See `docs/BARCODE_SETUP.md` for detailed configuration guide.

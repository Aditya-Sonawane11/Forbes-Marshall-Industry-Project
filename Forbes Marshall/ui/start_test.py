"""
Start Test Window
"""
import customtkinter as ctk
from tkinter import messagebox
import random
import logging
import traceback
import csv
import os
from datetime import datetime
from data.database import Database, DBRecord
from utils.serial_handler import SerialHandler
from typing import List, Optional

# Set up logger for this module
logger = logging.getLogger(__name__)

class StartTestWindow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, username: str, is_embedded: bool = False) -> None:
        super().__init__(parent)
        
        logger.info(f"Initializing StartTestWindow for user: {username}")
        self.username: str = username
        self.db: Database = Database()
        self.serial_handler: SerialHandler = SerialHandler()
        self.use_serial: bool = False
        
        # Create UI
        self.create_widgets()
        
        # Auto-focus on PCB ID field for barcode scanning
        self.after(100, lambda: self.pcb_id_entry.focus())
    
    def on_closing(self):
        """Handle window close"""
        if self.use_serial:
            self.serial_handler.disconnect()
        self.destroy()
    
    def on_pcb_id_change(self, event):
        """Handle PCB ID field changes"""
        pcb_id = self.pcb_id_entry.get().strip()
        if pcb_id:
            self.barcode_label.configure(text="✓ ID captured", text_color="green")
        else:
            self.barcode_label.configure(text="📷 Ready to scan", text_color="gray")
    
    def on_barcode_scanned(self, event):
        """Handle Enter key after barcode scan"""
        pcb_id = self.pcb_id_entry.get().strip()
        if pcb_id:
            self.barcode_label.configure(text="✓ Barcode scanned", text_color="green")
            # Auto-focus to next logical field or show ready message
            messagebox.showinfo("Barcode Scanned", f"PCB ID: {pcb_id}\n\nReady to run test!")
            # Focus on run test button area
            self.focus()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 800
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create test UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="PCB Testing",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # PCB ID
        pcb_frame = ctk.CTkFrame(container)
        pcb_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(pcb_frame, text="PCB ID:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.pcb_id_entry = ctk.CTkEntry(pcb_frame, width=300, placeholder_text="Scan barcode or enter PCB ID")
        self.pcb_id_entry.pack(side="left", padx=10)
        
        # Barcode indicator
        self.barcode_label = ctk.CTkLabel(
            pcb_frame,
            text="📷 Ready to scan",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.barcode_label.pack(side="left", padx=10)
        
        # Bind events for barcode scanning
        self.pcb_id_entry.bind('<KeyRelease>', self.on_pcb_id_change)
        self.pcb_id_entry.bind('<Return>', self.on_barcode_scanned)
        
        # Serial connection toggle
        serial_frame = ctk.CTkFrame(container)
        serial_frame.pack(pady=10, padx=20, fill="x")
        
        self.serial_switch = ctk.CTkSwitch(
            serial_frame,
            text="Use Serial Communication (Read from PCB)",
            command=self.toggle_serial
        )
        self.serial_switch.pack(side="left", padx=10)
        
        self.serial_status_label = ctk.CTkLabel(
            serial_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.serial_status_label.pack(side="left", padx=10)
        
        # Test Parameters Frame
        params_frame = ctk.CTkFrame(container)
        params_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            params_frame,
            text="Test Parameters",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Voltage
        voltage_frame = ctk.CTkFrame(params_frame)
        voltage_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(voltage_frame, text="Voltage (V):", width=150).pack(side="left", padx=10)
        self.voltage_entry = ctk.CTkEntry(voltage_frame, width=150, placeholder_text="e.g., 5.0")
        self.voltage_entry.pack(side="left", padx=10)
        ctk.CTkLabel(voltage_frame, text="Range: 4.5 - 5.5V", text_color="gray").pack(side="left", padx=10)
        
        # Current
        current_frame = ctk.CTkFrame(params_frame)
        current_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(current_frame, text="Current (A):", width=150).pack(side="left", padx=10)
        self.current_entry = ctk.CTkEntry(current_frame, width=150, placeholder_text="e.g., 0.5")
        self.current_entry.pack(side="left", padx=10)
        ctk.CTkLabel(current_frame, text="Range: 0.1 - 1.0A", text_color="gray").pack(side="left", padx=10)
        
        # Resistance
        resistance_frame = ctk.CTkFrame(params_frame)
        resistance_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(resistance_frame, text="Resistance (Ω):", width=150).pack(side="left", padx=10)
        self.resistance_entry = ctk.CTkEntry(resistance_frame, width=150, placeholder_text="e.g., 100")
        self.resistance_entry.pack(side="left", padx=10)
        ctk.CTkLabel(resistance_frame, text="Range: 90 - 110Ω", text_color="gray").pack(side="left", padx=10)
        
        # Notes
        notes_frame = ctk.CTkFrame(params_frame)
        notes_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(notes_frame, text="Notes:", width=150).pack(side="left", padx=10, anchor="n")
        self.notes_entry = ctk.CTkTextbox(notes_frame, width=400, height=80)
        self.notes_entry.pack(side="left", padx=10)
        
        # Result display
        self.result_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.result_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=20)
        
        run_test_btn = ctk.CTkButton(
            button_frame,
            text="Run Test",
            width=150,
            height=40,
            command=self.run_test
        )
        run_test_btn.pack(side="left", padx=10)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=150,
            height=40,
            fg_color="gray",
            command=self.clear_fields
        )
        clear_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=150,
            height=40,
            fg_color="red",
            hover_color="darkred",
            command=self.destroy
        )
        close_btn.pack(side="left", padx=10)
    
    def toggle_serial(self):
        """Toggle serial communication"""
        logger.info(f"CLICK: toggle_serial - Serial switch value: {self.serial_switch.get()}")
        
        if self.serial_switch.get():
            try:
                logger.info("Attempting to connect to serial port...")
                self.serial_handler.connect()
                self.use_serial = True
                self.serial_status_label.configure(text="✓ Connected", text_color="green")
                logger.info("✓ Serial connection successful!")
                
                # Disable manual entry when using serial
                self.voltage_entry.configure(state="disabled")
                self.current_entry.configure(state="disabled")
                self.resistance_entry.configure(state="disabled")
                logger.info("Manual entry fields disabled - reading from serial")
                
                messagebox.showinfo("Connected", "Serial connection established")
            except Exception as e:
                logger.error(f"ERROR: Serial connection failed")
                logger.error(f"Exception Type: {type(e).__name__}")
                logger.error(f"Error Message: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                
                self.serial_switch.deselect()
                self.use_serial = False
                self.serial_status_label.configure(text="✗ Failed", text_color="red")
                
                # Show custom error dialog with ports information
                error_msg = str(e)
                
                # Check if this is a port-related error
                if "No communication configuration" in error_msg or "Failed to connect" in error_msg:
                    logger.info("Showing ports error dialog")
                    # Create custom dialog showing available ports
                    self.show_ports_error_dialog(error_msg)
                else:
                    messagebox.showerror("Connection Error", error_msg)
        else:
            try:
                logger.info("Disconnecting from serial port...")
                self.serial_handler.disconnect()
                self.use_serial = False
                self.serial_status_label.configure(text="")
                logger.info("✓ Serial disconnected")
                
                # Re-enable manual entry
                self.voltage_entry.configure(state="normal")
                self.current_entry.configure(state="normal")
                self.resistance_entry.configure(state="normal")
                logger.info("Manual entry fields enabled")
            except Exception as e:
                logger.error(f"ERROR: Failed to disconnect serial")
                logger.error(f"Exception: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
    
    def show_ports_error_dialog(self, error_msg: str) -> None:
        """Show error dialog with available ports and port selector"""
        # Get available ports
        available_ports = self.serial_handler.get_available_ports()
        
        # Extract just port names (e.g., "COM17" from "COM17 (description)")
        port_names = [port.split()[0] if port else "" for port in available_ports]
        
        # Create error window
        error_window = ctk.CTkToplevel(self)
        error_window.title("Serial Connection Error")
        error_window.geometry("650x550")
        error_window.resizable(True, True)
        
        # Make window appear on top
        error_window.attributes('-topmost', True)
        error_window.lift()
        error_window.focus_force()
        error_window.grab_set()
        
        # Center the window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - 325
        y = (error_window.winfo_screenheight() // 2) - 275
        error_window.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(error_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Error title
        title_label = ctk.CTkLabel(
            main_frame,
            text="❌ Connection Failed",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="red"
        )
        title_label.pack(pady=10)
        
        # Error message
        msg_label = ctk.CTkLabel(
            main_frame,
            text=error_msg.split('\n')[0],  # Show only first line
            font=ctk.CTkFont(size=11),
            wraplength=550,
            justify="left"
        )
        msg_label.pack(pady=10, padx=10, anchor="w")
        
        # Port Selection Section
        selection_frame = ctk.CTkFrame(main_frame, fg_color="#2B2B2B")
        selection_frame.pack(pady=20, padx=10, fill="x")
        
        select_title = ctk.CTkLabel(
            selection_frame,
            text="Select COM Port:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        select_title.pack(pady=(15, 10), padx=15, anchor="w")
        
        # Port dropdown
        port_select_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
        port_select_frame.pack(pady=5, padx=15, fill="x")
        
        port_combo = ctk.CTkComboBox(
            port_select_frame,
            values=port_names if port_names else ["No ports available"],
            width=250,
            font=ctk.CTkFont(size=12)
        )
        if port_names:
            port_combo.set(port_names[0])  # Select first port by default
        port_combo.pack(side="left", padx=(0, 10))
        
        # Save & Connect button
        save_connect_btn = ctk.CTkButton(
            port_select_frame,
            text="Save & Connect",
            width=150,
            height=35,
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.save_and_connect_port(port_combo.get(), error_window)
        )
        save_connect_btn.pack(side="left")
        
        # Status label for feedback
        status_label = ctk.CTkLabel(
            selection_frame,
            text="",
            font=ctk.CTkFont(size=10)
        )
        status_label.pack(pady=(5, 15), padx=15, anchor="w")
        
        # Store status label for updates
        error_window.status_label = status_label
        
        # Available ports section
        ports_title = ctk.CTkLabel(
            main_frame,
            text="Available COM Ports:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        ports_title.pack(pady=(10, 5), anchor="w", padx=10)
        
        # Ports list frame
        ports_frame = ctk.CTkScrollableFrame(main_frame, height=100)
        ports_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        if available_ports:
            for port in available_ports:
                port_label = ctk.CTkLabel(
                    ports_frame,
                    text=f"• {port}",
                    font=ctk.CTkFont(size=11),
                    justify="left"
                )
                port_label.pack(anchor="w", padx=10, pady=3)
        else:
            no_ports_label = ctk.CTkLabel(
                ports_frame,
                text="No COM ports detected on this system",
                font=ctk.CTkFont(size=11),
                text_color="orange"
            )
            no_ports_label.pack(anchor="w", padx=10, pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=15)
        
        # Advanced Settings button
        config_btn = ctk.CTkButton(
            button_frame,
            text="Advanced Settings",
            width=150,
            fg_color="gray",
            command=lambda: self.open_communication_settings(error_window)
        )
        config_btn.pack(side="left", padx=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=100,
            fg_color="gray",
            command=error_window.destroy
        )
        close_btn.pack(side="left", padx=5)
    
    def run_test(self):
        """Run the PCB test"""
        logger.info("CLICK: run_test button")
        
        pcb_id = self.pcb_id_entry.get().strip()
        logger.info(f"PCB ID entered: {pcb_id}")
        
        if not pcb_id:
            logger.warning("ERROR: No PCB ID provided")
            messagebox.showerror("Error", "Please enter PCB ID")
            return
        
        logger.info(f"Starting test for PCB: {pcb_id}, Serial Mode: {self.use_serial}")
        
        if self.use_serial:
            # Read from serial
            try:
                logger.info("Reading test data from serial...")
                self.result_label.configure(text="Reading from PCB...", text_color="orange")
                self.update()
                
                test_data = self.serial_handler.read_test_data()
                voltage = test_data['voltage']
                current = test_data['current']
                resistance = test_data['resistance']
                logger.info(f"Serial data received: V={voltage}, C={current}, R={resistance}")
                # Update display
                self.voltage_entry.configure(state="normal")
                self.current_entry.configure(state="normal")
                self.resistance_entry.configure(state="normal")
                
                self.voltage_entry.delete(0, 'end')
                self.voltage_entry.insert(0, str(voltage))
                self.current_entry.delete(0, 'end')
                self.current_entry.insert(0, str(current))
                self.resistance_entry.delete(0, 'end')
                self.resistance_entry.insert(0, str(resistance))
                
                self.voltage_entry.configure(state="disabled")
                self.current_entry.configure(state="disabled")
                self.resistance_entry.configure(state="disabled")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read from PCB: {str(e)}")
                self.result_label.configure(text="")
                return
        else:
            # Manual entry
            try:
                voltage = float(self.voltage_entry.get())
                current = float(self.current_entry.get())
                resistance = float(self.resistance_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for all parameters")
                return
        
        # Test logic - check if values are within acceptable ranges
        voltage_ok = 4.5 <= voltage <= 5.5
        current_ok = 0.1 <= current <= 1.0
        resistance_ok = 90 <= resistance <= 110
        
        test_passed = voltage_ok and current_ok and resistance_ok
        
        # Get notes
        notes = self.notes_entry.get("1.0", "end-1c").strip()
        
        # Get user_id for save_test_result
        user_id = self.db.get_user_id(self.username)
        
        # Get test case ID (for now, use the first one or None)
        test_cases = self.db.get_test_cases()
        test_case_id = test_cases[0]['id'] if test_cases else None
        
        # Save to database with new signature
        status = "Pass" if test_passed else "Fail"
        result_id = self.db.save_test_result(
            test_case_id=test_case_id,
            user_id=user_id,
            pcb_serial_number=pcb_id,
            status=status,
            overall_pass=test_passed,
            notes=notes
        )
        
        logger.info(f"Test result saved with ID: {result_id}")
        
        # Save measured values as stage result for single test
        if result_id:
            try:
                # Get the first stage ID from test_stages table for this test case
                stage_id = None
                if test_case_id:
                    self.db.cursor.execute(
                        "SELECT id FROM test_stages WHERE test_case_id = %s ORDER BY stage_number LIMIT 1",
                        (test_case_id,)
                    )
                    stage_result = self.db.cursor.fetchone()
                    if stage_result:
                        stage_id = stage_result['id']
                    else:
                        # Create a default stage if none exists
                        logger.info(f"No stage found for test case {test_case_id}, creating default stage")
                        self.db.cursor.execute(
                            """INSERT INTO test_stages (test_case_id, stage_number, stage_name, description,
                               voltage_min, voltage_max, current_min, current_max, resistance_min, resistance_max)
                               VALUES (%s, 1, 'Default Stage', 'Auto-created stage for single PCB test',
                               0, 999, 0, 999, 0, 9999)""",
                            (test_case_id,)
                        )
                        self.db.conn.commit()
                        stage_id = self.db.cursor.lastrowid
                        logger.info(f"Created default stage with ID: {stage_id}")
                
                # If we found or created a stage_id, save the stage result
                if stage_id:
                    save_result = self.db.save_stage_result(
                        test_result_id=result_id,
                        stage_id=stage_id,
                        voltage_measured=voltage,
                        current_measured=current,
                        resistance_measured=resistance,
                        status=status,
                        failure_reason=""
                    )
                    if save_result:
                        logger.info(f"Stage result saved successfully with ID {save_result}: V={voltage}, C={current}, R={resistance}")
                    else:
                        logger.error(f"Stage result save returned None/False - check database errors")
                else:
                    logger.error(f"Could not find or create stage_id for test_case_id={test_case_id}")
            except Exception as e:
                logger.error(f"Failed to save stage result: {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
        
        # Log to CSV file automatically
        self.log_test_to_csv(pcb_id, voltage, current, resistance, status, test_passed)
        
        # Display result
        if test_passed:
            self.result_label.configure(text="✓ TEST PASSED", text_color="green")
            messagebox.showinfo("Success", f"PCB {pcb_id} passed all tests!")
        else:
            failed_params = []
            if not voltage_ok:
                failed_params.append("Voltage")
            if not current_ok:
                failed_params.append("Current")
            if not resistance_ok:
                failed_params.append("Resistance")
            
            self.result_label.configure(text="✗ TEST FAILED", text_color="red")
            messagebox.showerror(
                "Test Failed",
                f"PCB {pcb_id} failed!\nFailed parameters: {', '.join(failed_params)}"
            )
    
    def clear_fields(self):
        """Clear all input fields"""
        self.pcb_id_entry.delete(0, 'end')
        self.barcode_label.configure(text="📷 Ready to scan", text_color="gray")
        
        # Temporarily enable entries to clear them
        was_disabled = self.use_serial
        if was_disabled:
            self.voltage_entry.configure(state="normal")
            self.current_entry.configure(state="normal")
            self.resistance_entry.configure(state="normal")
        
        self.voltage_entry.delete(0, 'end')
        self.current_entry.delete(0, 'end')
        self.resistance_entry.delete(0, 'end')
        
        if was_disabled:
            self.voltage_entry.configure(state="disabled")
            self.current_entry.configure(state="disabled")
            self.resistance_entry.configure(state="disabled")
        
        self.notes_entry.delete("1.0", "end")
        self.result_label.configure(text="")
        
        # Re-focus on PCB ID for next scan
        self.pcb_id_entry.focus()
    
    def save_and_connect_port(self, selected_port: str, error_window: ctk.CTkToplevel) -> None:
        """Save selected port to configuration and attempt connection"""
        logger.info(f"CLICK: save_and_connect_port - Selected port: {selected_port}")
        
        if not selected_port or selected_port == "No ports available":
            logger.warning("No valid port selected")
            if hasattr(error_window, 'status_label'):
                error_window.status_label.configure(
                    text="❌ Please select a valid port",
                    text_color="red"
                )
            return
        
        try:
            # Update status
            if hasattr(error_window, 'status_label'):
                error_window.status_label.configure(
                    text="⏳ Saving configuration...",
                    text_color="orange"
                )
            error_window.update()
            
            # Get user ID
            user_id = self.db.get_user_id(self.username)
            
            # Get existing config or use defaults
            existing_config = self.db.get_comm_config()
            
            if existing_config:
                # Update existing config with new port
                baud_rate = existing_config.get('baud_rate', 9600)
                data_bits = existing_config.get('data_bits', 8)
                stop_bits = existing_config.get('stop_bits', 1)
                parity = existing_config.get('parity', 'None')
                timeout = existing_config.get('timeout_seconds') or existing_config.get('timeout', 5)
            else:
                # Use defaults
                baud_rate = 9600
                data_bits = 8
                stop_bits = 1
                parity = 'None'
                timeout = 5
            
            # Save new configuration
            logger.info(f"Saving configuration: Port={selected_port}, BaudRate={baud_rate}")
            config_id = self.db.save_comm_config(
                config_name="Auto-configured",
                com_port=selected_port,
                baud_rate=baud_rate,
                data_bits=data_bits,
                stop_bits=stop_bits,
                parity=parity,
                timeout_seconds=timeout,
                created_by=user_id
            )
            
            if not config_id:
                raise Exception("Failed to save configuration to database")
            
            logger.info(f"✓ Configuration saved with ID: {config_id}")
            
            # Update status
            if hasattr(error_window, 'status_label'):
                error_window.status_label.configure(
                    text="⏳ Connecting to port...",
                    text_color="orange"
                )
            error_window.update()
            
            # Attempt to connect
            self.serial_handler.connect()
            self.use_serial = True
            self.serial_status_label.configure(text="✓ Connected", text_color="green")
            
            # Disable manual entry when using serial
            self.voltage_entry.configure(state="disabled")
            self.current_entry.configure(state="disabled")
            self.resistance_entry.configure(state="disabled")
            
            # Enable the switch
            self.serial_switch.select()
            
            logger.info(f"✓ Successfully connected to {selected_port}")
            
            # Show success and close dialog
            messagebox.showinfo("Success", f"Connected to {selected_port} successfully!")
            error_window.destroy()
            
        except Exception as e:
            logger.error(f"Failed to save and connect: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            
            if hasattr(error_window, 'status_label'):
                error_window.status_label.configure(
                    text=f"❌ Failed: {str(e)[:50]}...",
                    text_color="red"
                )
            
            messagebox.showerror("Connection Failed", f"Failed to connect to {selected_port}:\n{str(e)}")
    
    def open_communication_settings(self, error_window: Optional[ctk.CTkToplevel] = None) -> None:
        """Open Communication Settings window from dashboard"""
        try:
            from ui.communication_config import CommunicationConfigWindow
            
            # Close error window if provided
            if error_window:
                error_window.destroy()
            
            logger.info("Opening Communication Settings window")
            
            # Get parent window (should be dashboard)
            parent = self.master
            while parent and not isinstance(parent, ctk.CTkToplevel):
                parent = parent.master
            
            # Create communication config window
            config_window = ctk.CTkToplevel(parent if parent else self)
            config_window.title("Communication Configuration")
            config_window.geometry("700x600")
            
            # Make window appear on top
            config_window.attributes('-topmost', True)
            config_window.lift()
            config_window.focus_force()
            config_window.grab_set()
            
            # Center window
            config_window.update_idletasks()
            x = (config_window.winfo_screenwidth() // 2) - 350
            y = (config_window.winfo_screenheight() // 2) - 300
            config_window.geometry(f"+{x}+{y}")
            
            # Create and pack the communication config frame
            config_frame = CommunicationConfigWindow(config_window, self.username, "admin")
            config_frame.pack(fill="both", expand=True)
            
        except Exception as e:
            logger.error(f"Failed to open Communication Settings: {str(e)}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            messagebox.showerror("Error", f"Failed to open Communication Settings:\n{str(e)}")
    
    def log_test_to_csv(self, pcb_id: str, voltage: float, current: float, resistance: float, 
                        status: str, test_passed: bool) -> None:
        """Log test results to CSV file automatically"""
        try:
            # Create logs directory if it doesn't exist
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Generate filename with date
            csv_filename = os.path.join(log_dir, f"test_results_{datetime.now().strftime('%Y%m%d')}.csv")
            
            # Check if file exists to determine if we need to write header
            file_exists = os.path.isfile(csv_filename)
            
            # Open file in append mode
            with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header if file is new
                if not file_exists:
                    writer.writerow([
                        'Timestamp', 'PCB ID', 'Tester', 'Status', 
                        'Voltage (V)', 'Current (A)', 'Resistance (Ω)', 
                        'Test Result', 'Notes'
                    ])
                
                # Get notes if available
                notes = self.notes_entry.get("1.0", "end-1c").strip() if hasattr(self, 'notes_entry') else ""
                
                # Write test data
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    pcb_id,
                    self.username,
                    status,
                    f"{voltage:.2f}",
                    f"{current:.2f}",
                    f"{resistance:.2f}",
                    "PASS" if test_passed else "FAIL",
                    notes
                ])
            
            logger.info(f"Test result logged to CSV: {csv_filename}")
            
        except Exception as e:
            logger.error(f"Failed to log test to CSV: {str(e)}")
            logger.error(traceback.format_exc())


"""
Start Test Window
"""
import customtkinter as ctk
from tkinter import messagebox
import random
import logging
import traceback
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
        """Show error dialog with available ports"""
        # Get available ports
        available_ports = self.serial_handler.get_available_ports()
        
        # Create error window
        error_window = ctk.CTkToplevel(self)
        error_window.title("Serial Connection Error")
        error_window.geometry("600x400")
        error_window.resizable(True, True)
        
        # Center the window
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - 300
        y = (error_window.winfo_screenheight() // 2) - 200
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
            text=error_msg,
            font=ctk.CTkFont(size=11),
            wraplength=550,
            justify="left"
        )
        msg_label.pack(pady=10, padx=10, anchor="w")
        
        # Available ports section
        ports_title = ctk.CTkLabel(
            main_frame,
            text="Available COM Ports:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        ports_title.pack(pady=(20, 5), anchor="w", padx=10)
        
        # Ports list frame
        ports_frame = ctk.CTkScrollableFrame(main_frame, height=150)
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
        
        # Instructions
        instr_label = ctk.CTkLabel(
            main_frame,
            text="→ Click 'Open Communication Settings' to configure the correct COM port",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            wraplength=550,
            justify="left"
        )
        instr_label.pack(pady=(10, 20), padx=10, anchor="w")
        
        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=10)
        
        # Configure settings button
        config_btn = ctk.CTkButton(
            button_frame,
            text="Open Communication Settings",
            width=180,
            fg_color="#0066cc",
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

"""
Start Test Window
"""
import customtkinter as ctk
from tkinter import messagebox
import random
from data.database import Database
from utils.serial_handler import SerialHandler

class StartTestWindow(ctk.CTkToplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        
        self.username = username
        self.db = Database()
        self.serial_handler = SerialHandler()
        self.use_serial = False
        
        self.title("Start Test")
        self.geometry("800x650")
        
        # Center window
        self.center_window()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        if self.serial_switch.get():
            try:
                self.serial_handler.connect()
                self.use_serial = True
                self.serial_status_label.configure(text="✓ Connected", text_color="green")
                
                # Disable manual entry when using serial
                self.voltage_entry.configure(state="disabled")
                self.current_entry.configure(state="disabled")
                self.resistance_entry.configure(state="disabled")
                
                messagebox.showinfo("Connected", "Serial connection established")
            except Exception as e:
                self.serial_switch.deselect()
                self.use_serial = False
                self.serial_status_label.configure(text="✗ Failed", text_color="red")
                messagebox.showerror("Connection Error", str(e))
        else:
            self.serial_handler.disconnect()
            self.use_serial = False
            self.serial_status_label.configure(text="")
            
            # Re-enable manual entry
            self.voltage_entry.configure(state="normal")
            self.current_entry.configure(state="normal")
            self.resistance_entry.configure(state="normal")
    
    def run_test(self):
        """Run the PCB test"""
        pcb_id = self.pcb_id_entry.get().strip()
        
        if not pcb_id:
            messagebox.showerror("Error", "Please enter PCB ID")
            return
        
        if self.use_serial:
            # Read from serial
            try:
                self.result_label.configure(text="Reading from PCB...", text_color="orange")
                self.update()
                
                test_data = self.serial_handler.read_test_data()
                voltage = test_data['voltage']
                current = test_data['current']
                resistance = test_data['resistance']
                
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
        
        # Save to database
        status = "PASS" if test_passed else "FAIL"
        self.db.save_test_result(pcb_id, self.username, status, voltage, current, resistance, notes)
        
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

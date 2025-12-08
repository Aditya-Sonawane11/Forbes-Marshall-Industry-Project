"""
Test Case Editor Window
"""
import customtkinter as ctk
from tkinter import messagebox
from data.database import Database

class TestCaseEditorWindow(ctk.CTkToplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.db = Database()
        
        self.title("Test Case Editor")
        self.geometry("900x700")
        
        self.center_window()
        self.create_widgets()
        self.load_test_cases()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 900
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create test case editor UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Test Case Editor",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Form frame
        form_frame = ctk.CTkFrame(container)
        form_frame.pack(pady=10, padx=20, fill="x")
        
        # PCB Type
        pcb_type_frame = ctk.CTkFrame(form_frame)
        pcb_type_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(pcb_type_frame, text="PCB Type:", width=150).pack(side="left", padx=10)
        self.pcb_type_entry = ctk.CTkEntry(pcb_type_frame, width=300, placeholder_text="e.g., Power Supply Board")
        self.pcb_type_entry.pack(side="left", padx=10)
        
        # Voltage Range
        voltage_frame = ctk.CTkFrame(form_frame)
        voltage_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(voltage_frame, text="Voltage Range (V):", width=150).pack(side="left", padx=10)
        self.voltage_min_entry = ctk.CTkEntry(voltage_frame, width=100, placeholder_text="Min")
        self.voltage_min_entry.pack(side="left", padx=5)
        ctk.CTkLabel(voltage_frame, text="-").pack(side="left", padx=5)
        self.voltage_max_entry = ctk.CTkEntry(voltage_frame, width=100, placeholder_text="Max")
        self.voltage_max_entry.pack(side="left", padx=5)
        
        # Current Range
        current_frame = ctk.CTkFrame(form_frame)
        current_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(current_frame, text="Current Range (A):", width=150).pack(side="left", padx=10)
        self.current_min_entry = ctk.CTkEntry(current_frame, width=100, placeholder_text="Min")
        self.current_min_entry.pack(side="left", padx=5)
        ctk.CTkLabel(current_frame, text="-").pack(side="left", padx=5)
        self.current_max_entry = ctk.CTkEntry(current_frame, width=100, placeholder_text="Max")
        self.current_max_entry.pack(side="left", padx=5)
        
        # Resistance Range
        resistance_frame = ctk.CTkFrame(form_frame)
        resistance_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(resistance_frame, text="Resistance Range (Ω):", width=150).pack(side="left", padx=10)
        self.resistance_min_entry = ctk.CTkEntry(resistance_frame, width=100, placeholder_text="Min")
        self.resistance_min_entry.pack(side="left", padx=5)
        ctk.CTkLabel(resistance_frame, text="-").pack(side="left", padx=5)
        self.resistance_max_entry = ctk.CTkEntry(resistance_frame, width=100, placeholder_text="Max")
        self.resistance_max_entry.pack(side="left", padx=5)
        
        # Description
        desc_frame = ctk.CTkFrame(form_frame)
        desc_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkLabel(desc_frame, text="Description:", width=150).pack(side="left", padx=10, anchor="n")
        self.description_entry = ctk.CTkTextbox(desc_frame, width=400, height=80)
        self.description_entry.pack(side="left", padx=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Test Case",
            width=150,
            height=40,
            command=self.save_test_case
        )
        save_btn.pack(side="left", padx=10)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=150,
            height=40,
            fg_color="gray",
            command=self.clear_fields
        )
        clear_btn.pack(side="left", padx=10)
        
        # Test cases list
        list_frame = ctk.CTkFrame(container)
        list_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            list_frame,
            text="Saved Test Cases",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Scrollable frame for test cases
        self.test_cases_scroll = ctk.CTkScrollableFrame(list_frame, height=200)
        self.test_cases_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Close button
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            width=150,
            height=40,
            fg_color="red",
            hover_color="darkred",
            command=self.destroy
        )
        close_btn.pack(pady=10)
    
    def save_test_case(self):
        """Save test case to database"""
        pcb_type = self.pcb_type_entry.get().strip()
        
        if not pcb_type:
            messagebox.showerror("Error", "Please enter PCB Type")
            return
        
        try:
            voltage_min = float(self.voltage_min_entry.get())
            voltage_max = float(self.voltage_max_entry.get())
            current_min = float(self.current_min_entry.get())
            current_max = float(self.current_max_entry.get())
            resistance_min = float(self.resistance_min_entry.get())
            resistance_max = float(self.resistance_max_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for all ranges")
            return
        
        description = self.description_entry.get("1.0", "end-1c").strip()
        
        success = self.db.save_test_case(
            pcb_type, voltage_min, voltage_max,
            current_min, current_max,
            resistance_min, resistance_max,
            description, self.username
        )
        
        if success:
            messagebox.showinfo("Success", f"Test case '{pcb_type}' saved successfully!")
            self.clear_fields()
            self.load_test_cases()
        else:
            messagebox.showerror("Error", "Failed to save test case")
    
    def clear_fields(self):
        """Clear all input fields"""
        self.pcb_type_entry.delete(0, 'end')
        self.voltage_min_entry.delete(0, 'end')
        self.voltage_max_entry.delete(0, 'end')
        self.current_min_entry.delete(0, 'end')
        self.current_max_entry.delete(0, 'end')
        self.resistance_min_entry.delete(0, 'end')
        self.resistance_max_entry.delete(0, 'end')
        self.description_entry.delete("1.0", "end")
    
    def load_test_cases(self):
        """Load and display test cases"""
        # Clear existing
        for widget in self.test_cases_scroll.winfo_children():
            widget.destroy()
        
        test_cases = self.db.get_test_cases()
        
        if not test_cases:
            ctk.CTkLabel(
                self.test_cases_scroll,
                text="No test cases saved yet",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for tc in test_cases:
            tc_frame = ctk.CTkFrame(self.test_cases_scroll)
            tc_frame.pack(pady=5, padx=10, fill="x")
            
            info_text = f"PCB Type: {tc[1]}\n"
            info_text += f"Voltage: {tc[2]}-{tc[3]}V | Current: {tc[4]}-{tc[5]}A | Resistance: {tc[6]}-{tc[7]}Ω\n"
            info_text += f"Description: {tc[8] if tc[8] else 'N/A'}"
            
            ctk.CTkLabel(
                tc_frame,
                text=info_text,
                justify="left",
                anchor="w"
            ).pack(side="left", padx=10, pady=10, fill="x", expand=True)
            
            delete_btn = ctk.CTkButton(
                tc_frame,
                text="Delete",
                width=80,
                fg_color="red",
                hover_color="darkred",
                command=lambda tc_id=tc[0]: self.delete_test_case(tc_id)
            )
            delete_btn.pack(side="right", padx=10)
    
    def delete_test_case(self, tc_id):
        """Delete a test case"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this test case?"):
            self.db.delete_test_case(tc_id)
            self.load_test_cases()
            messagebox.showinfo("Success", "Test case deleted")

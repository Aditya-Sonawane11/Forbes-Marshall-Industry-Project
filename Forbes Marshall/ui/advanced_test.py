"""
Advanced Test Window - Run multi-stage test sequences
"""
import customtkinter as ctk
from tkinter import messagebox
from data.database import Database
import time

class AdvancedTestWindow(ctk.CTkToplevel):
    def __init__(self, parent, username):
        super().__init__(parent)
        
        self.username = username
        self.db = Database()
        self.current_sequence = None
        self.test_running = False
        
        self.title("Advanced Test - Multi-Stage")
        self.geometry("900x700")
        
        self.center_window()
        self.create_widgets()
        self.load_sequences()
        
        # Auto-focus on PCB ID field for barcode scanning
        self.after(100, lambda: self.pcb_id_entry.focus())
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 900
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create advanced test UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Advanced Multi-Stage Testing",
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
        
        # Sequence selection
        seq_frame = ctk.CTkFrame(container)
        seq_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(seq_frame, text="Test Sequence:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.sequence_combo = ctk.CTkComboBox(
            seq_frame,
            values=["Select a sequence"],
            width=300,
            command=self.on_sequence_selected
        )
        self.sequence_combo.pack(side="left", padx=10)
        
        # Sequence info
        self.sequence_info_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sequence_info_label.pack(pady=5)
        
        # Test stages display
        stages_label = ctk.CTkLabel(
            container,
            text="Test Stages:",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stages_label.pack(pady=(20, 10))
        
        self.stages_frame = ctk.CTkScrollableFrame(container, height=300)
        self.stages_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Overall result
        self.overall_result_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.overall_result_label.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=20)
        
        self.run_test_btn = ctk.CTkButton(
            button_frame,
            text="Run Test Sequence",
            width=180,
            height=40,
            command=self.run_test_sequence,
            state="disabled"
        )
        self.run_test_btn.pack(side="left", padx=10)
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear",
            width=150,
            height=40,
            fg_color="gray",
            command=self.clear_all
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
    
    def load_sequences(self):
        """Load available test sequences"""
        sequences = self.db.get_test_sequences()
        
        if sequences:
            seq_names = [f"{seq[1]} ({seq[2]})" for seq in sequences]
            self.sequence_combo.configure(values=seq_names)
            self.sequences_data = sequences
        else:
            self.sequence_combo.configure(values=["No sequences available"])
            self.sequences_data = []
    
    def on_sequence_selected(self, choice):
        """Handle sequence selection"""
        if not self.sequences_data or choice == "Select a sequence":
            return
        
        # Find selected sequence
        for seq in self.sequences_data:
            if f"{seq[1]} ({seq[2]})" == choice:
                self.current_sequence = seq
                break
        
        if self.current_sequence:
            self.sequence_info_label.configure(
                text=f"PCB Type: {self.current_sequence[2]} | Total Stages: {self.current_sequence[3]}"
            )
            self.display_stages()
            self.run_test_btn.configure(state="normal")
    
    def display_stages(self):
        """Display test stages"""
        for widget in self.stages_frame.winfo_children():
            widget.destroy()
        
        if not self.current_sequence:
            return
        
        stages = self.db.get_sequence_stages(self.current_sequence[0])
        
        for idx, stage in enumerate(stages):
            stage_frame = ctk.CTkFrame(self.stages_frame)
            stage_frame.pack(pady=5, padx=10, fill="x")
            
            # Stage header
            header_frame = ctk.CTkFrame(stage_frame)
            header_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                header_frame,
                text=f"Stage {idx + 1}: {stage[2]}",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="left", padx=10)
            
            # Status label (will be updated during test)
            status_label = ctk.CTkLabel(
                header_frame,
                text="⏳ Pending",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            status_label.pack(side="right", padx=10)
            
            # Store reference for updating
            stage_frame.status_label = status_label
            stage_frame.stage_data = stage
            
            # Stage parameters
            params_text = f"V: {stage[3]}-{stage[4]}V | C: {stage[5]}-{stage[6]}A | R: {stage[7]}-{stage[8]}Ω"
            ctk.CTkLabel(
                stage_frame,
                text=params_text,
                text_color="gray"
            ).pack(padx=10, pady=5)
    
    def run_test_sequence(self):
        """Run the multi-stage test sequence"""
        pcb_id = self.pcb_id_entry.get().strip()
        
        if not pcb_id:
            messagebox.showerror("Error", "Please enter PCB ID")
            return
        
        if not self.current_sequence:
            messagebox.showerror("Error", "Please select a test sequence")
            return
        
        self.test_running = True
        self.run_test_btn.configure(state="disabled")
        self.overall_result_label.configure(text="Testing in progress...", text_color="orange")
        
        # Get all stages
        stages = self.db.get_sequence_stages(self.current_sequence[0])
        all_passed = True
        failed_stages = []
        
        # Run each stage
        for idx, stage_widget in enumerate(self.stages_frame.winfo_children()):
            if not hasattr(stage_widget, 'stage_data'):
                continue
            
            stage = stage_widget.stage_data
            
            # Update status to running
            stage_widget.status_label.configure(text="🔄 Running...", text_color="orange")
            self.update()
            
            # Simulate test (in real implementation, this would read from hardware)
            # For demo, we'll use random values within a range
            import random
            voltage = random.uniform(stage[3] - 0.5, stage[4] + 0.5)
            current = random.uniform(stage[5] - 0.1, stage[6] + 0.1)
            resistance = random.uniform(stage[7] - 5, stage[8] + 5)
            
            # Check if values are within range
            voltage_ok = stage[3] <= voltage <= stage[4]
            current_ok = stage[5] <= current <= stage[6]
            resistance_ok = stage[7] <= resistance <= stage[8]
            
            stage_passed = voltage_ok and current_ok and resistance_ok
            
            # Update stage status
            if stage_passed:
                stage_widget.status_label.configure(text="✓ PASS", text_color="green")
            else:
                stage_widget.status_label.configure(text="✗ FAIL", text_color="red")
                all_passed = False
                failed_stages.append(f"Stage {idx + 1}: {stage[2]}")
            
            self.update()
            time.sleep(0.5)  # Simulate test duration
        
        # Save overall result
        overall_status = "PASS" if all_passed else "FAIL"
        notes = f"Multi-stage test: {self.current_sequence[1]}"
        if failed_stages:
            notes += f" | Failed stages: {', '.join(failed_stages)}"
        
        # Save to database (using average values for simplicity)
        self.db.save_test_result(
            pcb_id, self.username, overall_status,
            5.0, 0.5, 100.0,  # Placeholder values
            notes
        )
        
        # Display overall result
        if all_passed:
            self.overall_result_label.configure(
                text="✓ ALL STAGES PASSED",
                text_color="green"
            )
            messagebox.showinfo("Success", f"PCB {pcb_id} passed all test stages!")
        else:
            self.overall_result_label.configure(
                text="✗ TEST FAILED",
                text_color="red"
            )
            messagebox.showerror(
                "Test Failed",
                f"PCB {pcb_id} failed!\n\nFailed stages:\n" + "\n".join(failed_stages)
            )
        
        self.test_running = False
        self.run_test_btn.configure(state="normal")
    
    def clear_all(self):
        """Clear all fields and reset"""
        self.pcb_id_entry.delete(0, 'end')
        self.barcode_label.configure(text="📷 Ready to scan", text_color="gray")
        self.sequence_combo.set("Select a sequence")
        self.current_sequence = None
        self.sequence_info_label.configure(text="")
        self.overall_result_label.configure(text="")
        self.run_test_btn.configure(state="disabled")
        
        for widget in self.stages_frame.winfo_children():
            widget.destroy()
        
        # Re-focus on PCB ID for next scan
        self.pcb_id_entry.focus()
    
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
            # Auto-focus to sequence selection
            self.sequence_combo.focus()

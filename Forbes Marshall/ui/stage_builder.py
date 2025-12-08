"""
Stage Builder Window - Create multi-stage test sequences
"""
import customtkinter as ctk
from tkinter import messagebox
from data.database import Database

class StageBuilderWindow(ctk.CTkToplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.db = Database()
        self.stages = []
        
        self.title("Stage Builder")
        self.geometry("1000x750")
        
        self.center_window()
        self.create_widgets()
        self.load_sequences()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 1000
        height = 750
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create stage builder UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Stage Builder - Multi-Stage Test Sequences",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Two column layout
        content_frame = ctk.CTkFrame(container)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side - Create new sequence
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            left_frame,
            text="Create Test Sequence",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Sequence name
        name_frame = ctk.CTkFrame(left_frame)
        name_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(name_frame, text="Sequence Name:", width=120).pack(side="left", padx=5)
        self.sequence_name_entry = ctk.CTkEntry(name_frame, width=250, placeholder_text="e.g., Full PCB Test")
        self.sequence_name_entry.pack(side="left", padx=5)
        
        # PCB Type
        pcb_frame = ctk.CTkFrame(left_frame)
        pcb_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(pcb_frame, text="PCB Type:", width=120).pack(side="left", padx=5)
        self.pcb_type_entry = ctk.CTkEntry(pcb_frame, width=250, placeholder_text="e.g., Power Board")
        self.pcb_type_entry.pack(side="left", padx=5)
        
        # Stage configuration
        stage_config_frame = ctk.CTkFrame(left_frame)
        stage_config_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            stage_config_frame,
            text="Add Test Stage",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Stage name
        stage_name_frame = ctk.CTkFrame(stage_config_frame)
        stage_name_frame.pack(pady=5, fill="x", padx=10)
        
        ctk.CTkLabel(stage_name_frame, text="Stage Name:", width=100).pack(side="left", padx=5)
        self.stage_name_entry = ctk.CTkEntry(stage_name_frame, width=200, placeholder_text="e.g., Power-On Test")
        self.stage_name_entry.pack(side="left", padx=5)
        
        # Test parameters
        params_frame = ctk.CTkFrame(stage_config_frame)
        params_frame.pack(pady=5, fill="x", padx=10)
        
        # Voltage
        v_frame = ctk.CTkFrame(params_frame)
        v_frame.pack(pady=3, fill="x")
        ctk.CTkLabel(v_frame, text="Voltage (V):", width=100).pack(side="left", padx=5)
        self.stage_v_min = ctk.CTkEntry(v_frame, width=70, placeholder_text="Min")
        self.stage_v_min.pack(side="left", padx=2)
        ctk.CTkLabel(v_frame, text="-").pack(side="left")
        self.stage_v_max = ctk.CTkEntry(v_frame, width=70, placeholder_text="Max")
        self.stage_v_max.pack(side="left", padx=2)
        
        # Current
        c_frame = ctk.CTkFrame(params_frame)
        c_frame.pack(pady=3, fill="x")
        ctk.CTkLabel(c_frame, text="Current (A):", width=100).pack(side="left", padx=5)
        self.stage_c_min = ctk.CTkEntry(c_frame, width=70, placeholder_text="Min")
        self.stage_c_min.pack(side="left", padx=2)
        ctk.CTkLabel(c_frame, text="-").pack(side="left")
        self.stage_c_max = ctk.CTkEntry(c_frame, width=70, placeholder_text="Max")
        self.stage_c_max.pack(side="left", padx=2)
        
        # Resistance
        r_frame = ctk.CTkFrame(params_frame)
        r_frame.pack(pady=3, fill="x")
        ctk.CTkLabel(r_frame, text="Resistance (Ω):", width=100).pack(side="left", padx=5)
        self.stage_r_min = ctk.CTkEntry(r_frame, width=70, placeholder_text="Min")
        self.stage_r_min.pack(side="left", padx=2)
        ctk.CTkLabel(r_frame, text="-").pack(side="left")
        self.stage_r_max = ctk.CTkEntry(r_frame, width=70, placeholder_text="Max")
        self.stage_r_max.pack(side="left", padx=2)
        
        # Add stage button
        add_stage_btn = ctk.CTkButton(
            stage_config_frame,
            text="Add Stage",
            width=150,
            command=self.add_stage
        )
        add_stage_btn.pack(pady=10)
        
        # Current stages list
        ctk.CTkLabel(
            left_frame,
            text="Stages in Sequence:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        self.stages_list_frame = ctk.CTkScrollableFrame(left_frame, height=150)
        self.stages_list_frame.pack(pady=5, padx=20, fill="both")
        
        # Save sequence button
        save_seq_btn = ctk.CTkButton(
            left_frame,
            text="Save Sequence",
            width=200,
            height=40,
            command=self.save_sequence
        )
        save_seq_btn.pack(pady=10)
        
        # Right side - Saved sequences
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(
            right_frame,
            text="Saved Test Sequences",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        self.sequences_scroll = ctk.CTkScrollableFrame(right_frame)
        self.sequences_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
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
    
    def add_stage(self):
        """Add a stage to the current sequence"""
        stage_name = self.stage_name_entry.get().strip()
        
        if not stage_name:
            messagebox.showerror("Error", "Please enter stage name")
            return
        
        try:
            v_min = float(self.stage_v_min.get())
            v_max = float(self.stage_v_max.get())
            c_min = float(self.stage_c_min.get())
            c_max = float(self.stage_c_max.get())
            r_min = float(self.stage_r_min.get())
            r_max = float(self.stage_r_max.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
            return
        
        stage = {
            'name': stage_name,
            'voltage_min': v_min,
            'voltage_max': v_max,
            'current_min': c_min,
            'current_max': c_max,
            'resistance_min': r_min,
            'resistance_max': r_max
        }
        
        self.stages.append(stage)
        self.update_stages_list()
        self.clear_stage_fields()
    
    def clear_stage_fields(self):
        """Clear stage input fields"""
        self.stage_name_entry.delete(0, 'end')
        self.stage_v_min.delete(0, 'end')
        self.stage_v_max.delete(0, 'end')
        self.stage_c_min.delete(0, 'end')
        self.stage_c_max.delete(0, 'end')
        self.stage_r_min.delete(0, 'end')
        self.stage_r_max.delete(0, 'end')
    
    def update_stages_list(self):
        """Update the display of current stages"""
        for widget in self.stages_list_frame.winfo_children():
            widget.destroy()
        
        if not self.stages:
            ctk.CTkLabel(
                self.stages_list_frame,
                text="No stages added yet",
                text_color="gray"
            ).pack(pady=10)
            return
        
        for idx, stage in enumerate(self.stages):
            stage_frame = ctk.CTkFrame(self.stages_list_frame)
            stage_frame.pack(pady=3, padx=5, fill="x")
            
            stage_text = f"{idx + 1}. {stage['name']}"
            ctk.CTkLabel(
                stage_frame,
                text=stage_text,
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=10)
            
            remove_btn = ctk.CTkButton(
                stage_frame,
                text="Remove",
                width=70,
                fg_color="red",
                hover_color="darkred",
                command=lambda i=idx: self.remove_stage(i)
            )
            remove_btn.pack(side="right", padx=5)
    
    def remove_stage(self, index):
        """Remove a stage from the sequence"""
        self.stages.pop(index)
        self.update_stages_list()
    
    def save_sequence(self):
        """Save the test sequence"""
        sequence_name = self.sequence_name_entry.get().strip()
        pcb_type = self.pcb_type_entry.get().strip()
        
        if not sequence_name:
            messagebox.showerror("Error", "Please enter sequence name")
            return
        
        if not pcb_type:
            messagebox.showerror("Error", "Please enter PCB type")
            return
        
        if not self.stages:
            messagebox.showerror("Error", "Please add at least one stage")
            return
        
        success = self.db.save_test_sequence(sequence_name, pcb_type, self.stages, self.username)
        
        if success:
            messagebox.showinfo("Success", f"Test sequence '{sequence_name}' saved successfully!")
            self.sequence_name_entry.delete(0, 'end')
            self.pcb_type_entry.delete(0, 'end')
            self.stages = []
            self.update_stages_list()
            self.load_sequences()
        else:
            messagebox.showerror("Error", "Failed to save sequence")
    
    def load_sequences(self):
        """Load and display saved sequences"""
        for widget in self.sequences_scroll.winfo_children():
            widget.destroy()
        
        sequences = self.db.get_test_sequences()
        
        if not sequences:
            ctk.CTkLabel(
                self.sequences_scroll,
                text="No sequences saved yet",
                text_color="gray"
            ).pack(pady=20)
            return
        
        for seq in sequences:
            seq_frame = ctk.CTkFrame(self.sequences_scroll)
            seq_frame.pack(pady=5, padx=10, fill="x")
            
            # Sequence info
            info_frame = ctk.CTkFrame(seq_frame)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=seq[1],
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                info_frame,
                text=f"PCB Type: {seq[2]} | Stages: {seq[3]}",
                text_color="gray"
            ).pack(anchor="w")
            
            # Buttons
            btn_frame = ctk.CTkFrame(seq_frame)
            btn_frame.pack(side="right", padx=10)
            
            view_btn = ctk.CTkButton(
                btn_frame,
                text="View",
                width=70,
                command=lambda s=seq: self.view_sequence(s)
            )
            view_btn.pack(side="left", padx=3)
            
            delete_btn = ctk.CTkButton(
                btn_frame,
                text="Delete",
                width=70,
                fg_color="red",
                hover_color="darkred",
                command=lambda s_id=seq[0]: self.delete_sequence(s_id)
            )
            delete_btn.pack(side="left", padx=3)
    
    def view_sequence(self, sequence):
        """View sequence details"""
        details_window = ctk.CTkToplevel(self)
        details_window.title(f"Sequence: {sequence[1]}")
        details_window.geometry("600x500")
        
        # Center window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - 300
        y = (details_window.winfo_screenheight() // 2) - 250
        details_window.geometry(f'600x500+{x}+{y}')
        
        container = ctk.CTkFrame(details_window)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text=sequence[1],
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            container,
            text=f"PCB Type: {sequence[2]}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        ctk.CTkLabel(
            container,
            text="Test Stages:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 10))
        
        stages_scroll = ctk.CTkScrollableFrame(container, height=300)
        stages_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        stages = self.db.get_sequence_stages(sequence[0])
        
        for idx, stage in enumerate(stages):
            stage_frame = ctk.CTkFrame(stages_scroll)
            stage_frame.pack(pady=5, padx=10, fill="x")
            
            stage_text = f"Stage {idx + 1}: {stage[2]}\n"
            stage_text += f"Voltage: {stage[3]}-{stage[4]}V | "
            stage_text += f"Current: {stage[5]}-{stage[6]}A | "
            stage_text += f"Resistance: {stage[7]}-{stage[8]}Ω"
            
            ctk.CTkLabel(
                stage_frame,
                text=stage_text,
                justify="left"
            ).pack(padx=10, pady=10)
        
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            width=150,
            command=details_window.destroy
        )
        close_btn.pack(pady=10)
    
    def delete_sequence(self, seq_id):
        """Delete a test sequence"""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this sequence?"):
            self.db.delete_test_sequence(seq_id)
            self.load_sequences()
            messagebox.showinfo("Success", "Sequence deleted")

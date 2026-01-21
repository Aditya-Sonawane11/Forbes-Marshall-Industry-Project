"""
Advanced Test Window - Run multi-stage test sequences
"""
import customtkinter as ctk
from tkinter import messagebox
from data.database import Database, DBRecord
import time
import logging
import traceback
from typing import List, Dict, Any, Optional

# Set up logger for this module
logger = logging.getLogger(__name__)

class AdvancedTestWindow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, username: str, is_embedded: bool = False) -> None:
        super().__init__(parent)
        
        logger.info("Initializing AdvancedTestWindow")
        self.username: str = username
        self.db: Database = Database()
        self.current_sequence: Optional[DBRecord] = None
        self.test_running: bool = False
        self.stages_widgets: List[Dict[str, Any]] = []  # Store references to stage widgets
        self.sequences_data: List[DBRecord] = []
        
        self.create_widgets()
        self.load_sequences()
        
        # Auto-focus on PCB ID field for barcode scanning
        self.after(100, lambda: self.pcb_id_entry.focus())
    
    def center_window(self) -> None:
        """Placeholder for compatibility"""
        pass
        x: int = (self.winfo_screenwidth() // 2) - (width // 2)
        y: int = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self) -> None:
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
    
    def load_sequences(self) -> None:
        """Load available test sequences"""
        sequences: List[DBRecord] = self.db.get_test_cases()
        
        if sequences:
            seq_names = [f"{seq['name']} ({seq.get('description', 'N/A')})" for seq in sequences]
            self.sequence_combo.configure(values=seq_names)
            self.sequences_data = sequences
        else:
            self.sequence_combo.configure(values=["No sequences available"])
            self.sequences_data = []
    
    def on_sequence_selected(self, choice: str) -> None:
        """Handle sequence selection"""
        if not self.sequences_data or choice == "Select a sequence":
            return
        
        # Find selected sequence
        for seq in self.sequences_data:
            seq_name: str = seq['name']
            seq_desc: str = seq.get('description', 'N/A')
            if f"{seq_name} ({seq_desc})" == choice:
                self.current_sequence = seq
                break
        
        if self.current_sequence:
            # Get stages to count them
            stages = self.db.get_test_stages(self.current_sequence['id'])
            stage_count = len(stages) if stages else 0
            self.sequence_info_label.configure(
                text=f"PCB Type: {self.current_sequence.get('description', 'N/A')} | Total Stages: {stage_count}"
            )
            self.display_stages()
            self.run_test_btn.configure(state="normal")
    
    def display_stages(self) -> None:
        """Display test stages"""
        for widget in self.stages_frame.winfo_children():
            widget.destroy()
        
        self.stages_widgets = []  # Clear the list
        
        if not self.current_sequence:
            return
        
        stages: List[DBRecord] = self.db.get_test_stages(self.current_sequence['id'])
        
        # If no stages from database, show message
        if not stages:
            ctk.CTkLabel(
                self.stages_frame,
                text="No test stages configured for this sequence",
                text_color="orange",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
            return
        
        for idx, stage in enumerate(stages):
            try:
                stage_frame = ctk.CTkFrame(self.stages_frame)
                stage_frame.pack(pady=5, padx=10, fill="x")
                
                # Stage header
                header_frame = ctk.CTkFrame(stage_frame)
                header_frame.pack(fill="x", padx=10, pady=5)
                
                # Use stage_name from database or name from dictionary
                stage_display_name = stage.get('stage_name') or stage.get('name', 'Unknown')
                ctk.CTkLabel(
                    header_frame,
                    text=f"Stage {idx + 1}: {stage_display_name}",
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
                stage_info = {
                    'frame': stage_frame,
                    'status_label': status_label,
                    'stage_data': stage,
                    'index': idx
                }
                self.stages_widgets.append(stage_info)
                
                # Stage parameters - handle missing fields gracefully
                v_min = stage.get('voltage_min', 0)
                v_max = stage.get('voltage_max', 0)
                c_min = stage.get('current_min', 0)
                c_max = stage.get('current_max', 0)
                r_min = stage.get('resistance_min', 0)
                r_max = stage.get('resistance_max', 0)
                
                params_text = f"V: {v_min}-{v_max}V | C: {c_min}-{c_max}A | R: {r_min}-{r_max}Ω"
                ctk.CTkLabel(
                    stage_frame,
                    text=params_text,
                    text_color="gray"
                ).pack(padx=10, pady=5)
            except Exception as e:
                print(f"Error displaying stage {idx + 1}: {e}")
                ctk.CTkLabel(
                    self.stages_frame,
                    text=f"Error loading stage {idx + 1}",
                    text_color="red"
                ).pack(pady=5)
    
    def run_test_sequence(self) -> None:
        """Run the multi-stage test sequence"""
        logger.info("=" * 60)
        logger.info("CLICK: run_test_sequence button")
        
        pcb_id: str = self.pcb_id_entry.get().strip()
        logger.info(f"PCB ID: {pcb_id}")
        
        if not pcb_id:
            logger.error("ERROR: No PCB ID provided")
            messagebox.showerror("Error", "Please enter PCB ID")
            return
        
        if not self.current_sequence:
            logger.error("ERROR: No test sequence selected")
            messagebox.showerror("Error", "Please select a test sequence")
            return
        
        logger.info(f"Starting test sequence: {self.current_sequence['name']}")
        self.test_running = True
        self.run_test_btn.configure(state="disabled")
        self.overall_result_label.configure(text="Testing in progress...", text_color="orange")
        
        # Get all stages
        stages = self.db.get_test_stages(self.current_sequence['id'])
        logger.info(f"Total stages to run: {len(stages)}")
        all_passed = True
        failed_stages = []
        
        # Run each stage
        for stage_info in self.stages_widgets:
            try:
                # Update status to running
                stage_info['status_label'].configure(text="🔄 Running...", text_color="orange")
                self.update()
                
                stage = stage_info['stage_data']
                idx = stage_info['index']
                stage_name = stage.get('stage_name') or stage.get('name', f'Stage {idx + 1}')
                
                logger.info(f"Running {stage_name}...")
                
                # Simulate test (in real implementation, this would read from hardware)
                # For demo, we'll use random values within a range
                import random
                voltage = random.uniform(float(stage['voltage_min']) - 0.5, float(stage['voltage_max']) + 0.5)
                current = random.uniform(float(stage['current_min']) - 0.1, float(stage['current_max']) + 0.1)
                resistance = random.uniform(float(stage['resistance_min']) - 5, float(stage['resistance_max']) + 5)
                
                logger.info(f"Measured values - V: {voltage:.2f}V (range: {stage['voltage_min']}-{stage['voltage_max']}), C: {current:.2f}A, R: {resistance:.2f}Ω")
                
                # Store measured values in stage_info for later saving
                stage_info['voltage_measured'] = voltage
                stage_info['current_measured'] = current
                stage_info['resistance_measured'] = resistance
                
                # Check if values are within range
                voltage_ok = stage['voltage_min'] <= voltage <= stage['voltage_max']
                current_ok = stage['current_min'] <= current <= stage['current_max']
                resistance_ok = stage['resistance_min'] <= resistance <= stage['resistance_max']
                
                stage_passed = voltage_ok and current_ok and resistance_ok
                
                # Store status in stage_info for later saving
                stage_info['stage_status'] = 'PASS' if stage_passed else 'FAIL'
                if not stage_passed:
                    if not voltage_ok:
                        stage_info['failure_reason'] = f'Voltage out of range: {voltage:.2f}V'
                    elif not current_ok:
                        stage_info['failure_reason'] = f'Current out of range: {current:.2f}A'
                    elif not resistance_ok:
                        stage_info['failure_reason'] = f'Resistance out of range: {resistance:.2f}Ω'
                
                # Update stage status
                if stage_passed:
                    logger.info(f"✓ {stage_name} PASSED")
                    stage_info['status_label'].configure(text="✓ PASS", text_color="green")
                else:
                    logger.warning(f"✗ {stage_name} FAILED - {stage_info.get('failure_reason', 'Unknown')}")
                    stage_info['status_label'].configure(text="✗ FAIL", text_color="red")
                    all_passed = False
                    failed_stages.append(f"Stage {idx + 1}: {stage_name}")
                
                self.update()
                time.sleep(0.5)  # Simulate test duration
                
            except Exception as e:
                logger.error(f"ERROR in stage {stage_info['index']}: {str(e)}")
                logger.error(f"Traceback:\n{traceback.format_exc()}")
                stage_info['status_label'].configure(text="✗ ERROR", text_color="red")
                all_passed = False
        
        # Save overall result
        overall_status = "PASS" if all_passed else "FAIL"
        notes = f"Multi-stage test: {self.current_sequence['name']}"
        if failed_stages:
            notes += f" | Failed stages: {', '.join(failed_stages)}"
        
        logger.info(f"Test sequence completed - Overall result: {overall_status}")
        logger.info(f"Details: {notes}")
        
        # Save to database
        test_case_id: int = self.current_sequence['id']
        user_id: Optional[int] = self.db.get_user_id(self.username)
        
        # Collect stage measurements for saving
        stage_measurements: List[Dict[str, Any]] = []
        for stage_info in self.stages_widgets:
            stage = stage_info['stage_data']
            stage_measurements.append({
                'stage_id': stage.get('id'),
                'voltage': stage_info.get('voltage_measured', 0),
                'current': stage_info.get('current_measured', 0),
                'resistance': stage_info.get('resistance_measured', 0),
                'status': stage_info.get('stage_status', 'FAIL')
            })
        
        test_result_id = self.db.save_test_result(
            test_case_id=test_case_id,
            user_id=user_id,
            pcb_serial_number=pcb_id,
            status=overall_status,
            overall_pass=all_passed,
            notes=notes
        )
        
        # Save individual stage results
        if test_result_id:
            for idx, stage_info in enumerate(self.stages_widgets):
                stage = stage_info['stage_data']
                self.db.save_stage_result(
                    test_result_id=test_result_id,
                    stage_id=stage.get('id'),
                    voltage_measured=stage_info.get('voltage_measured', 0),
                    current_measured=stage_info.get('current_measured', 0),
                    resistance_measured=stage_info.get('resistance_measured', 0),
                    status=stage_info.get('stage_status', 'FAIL'),
                    failure_reason=stage_info.get('failure_reason')
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
    
    def clear_all(self) -> None:
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
        
        self.stages_widgets = []  # Clear the list
        
        # Re-focus on PCB ID for next scan
        self.pcb_id_entry.focus()
    
    def on_pcb_id_change(self, event) -> None:
        """Handle PCB ID field changes"""
        pcb_id: str = self.pcb_id_entry.get().strip()
        if pcb_id:
            self.barcode_label.configure(text="✓ ID captured", text_color="green")
        else:
            self.barcode_label.configure(text="📷 Ready to scan", text_color="gray")
    
    def on_barcode_scanned(self, event) -> None:
        """Handle Enter key after barcode scan"""
        pcb_id: str = self.pcb_id_entry.get().strip()
        if pcb_id:
            self.barcode_label.configure(text="✓ Barcode scanned", text_color="green")
            # Auto-focus to sequence selection
            self.sequence_combo.focus()

"""
Results History Window
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from data.database import Database, DBRecord
import csv
from datetime import datetime
from typing import List, Dict, Any

class ResultsHistoryWindow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, username: str, role: str, is_embedded: bool = False) -> None:
        super().__init__(parent)
        
        self.username: str = username
        self.role: str = role
        self.db: Database = Database()
        
        self.create_widgets()
        self.load_results()
    
    def center_window(self) -> None:
        """Placeholder for compatibility"""
        pass
    
    def create_widgets(self) -> None:
        """Create results history UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Test Results History",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Filter frame
        filter_frame = ctk.CTkFrame(container)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        # Status filter
        ctk.CTkLabel(filter_frame, text="Filter by Status:").pack(side="left", padx=10)
        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["All", "PASS", "FAIL"],
            width=150,
            command=self.load_results
        )
        self.status_filter.set("All")
        self.status_filter.pack(side="left", padx=10)
        
        # Search by PCB ID
        ctk.CTkLabel(filter_frame, text="Search PCB ID:").pack(side="left", padx=10)
        self.search_entry = ctk.CTkEntry(filter_frame, width=200, placeholder_text="Enter PCB ID")
        self.search_entry.pack(side="left", padx=10)
        
        search_btn = ctk.CTkButton(
            filter_frame,
            text="Search",
            width=100,
            command=self.load_results
        )
        search_btn.pack(side="left", padx=10)
        
        # Export button
        export_btn = ctk.CTkButton(
            filter_frame,
            text="Export to CSV",
            width=150,
            command=self.export_to_csv
        )
        export_btn.pack(side="right", padx=10)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(container)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.stats_label.pack(pady=10)
        
        # Results list
        list_frame = ctk.CTkFrame(container)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        headers = ["PCB ID", "Tester", "Status", "Voltage", "Current", "Resistance", "Date/Time", "Actions"]
        widths = [100, 100, 80, 80, 80, 100, 150, 100]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=width
            ).pack(side="left", padx=5)
        
        # Scrollable results
        self.results_scroll = ctk.CTkScrollableFrame(list_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
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
    
    def load_results(self, *args) -> None:
        """Load and display test results"""
        # Clear existing
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Get filters
        status_filter: str = self.status_filter.get()
        search_query: str = self.search_entry.get().strip()
        
        # Get results based on role
        results: List[DBRecord] = self.db.get_test_results()
        if self.role == "tester":
            # Need to get actual username, not just filter by role
            results = [r for r in results if r.get('user_id') == self.db.get_user_id(self.username)]
        
        # Apply filters
        if status_filter != "All":
            results = [r for r in results if r.get('status') == status_filter]
        
        if search_query:
            results = [r for r in results if search_query.lower() in str(r.get('pcb_serial_number', '')).lower()]
        
        # Update stats
        total = len(results)
        passed = len([r for r in results if r['status'] == "Pass"])
        failed = len([r for r in results if r['status'] == "Fail"])
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        self.stats_label.configure(
            text=f"Total Tests: {total} | Passed: {passed} | Failed: {failed} | Pass Rate: {pass_rate:.1f}%"
        )
        
        if not results:
            ctk.CTkLabel(
                self.results_scroll,
                text="No test results found",
                text_color="gray"
            ).pack(pady=20)
            return
        
        # Display results
        for result in results:
            result_frame = ctk.CTkFrame(self.results_scroll)
            result_frame.pack(pady=2, padx=5, fill="x")
            
            # Get stage results for measured values
            stage_results = self.db.get_stage_results(result['id'])
            voltage_val = None
            current_val = None
            resistance_val = None
            
            if stage_results and len(stage_results) > 0:
                first_stage = stage_results[0]
                voltage_val = first_stage.get('voltage_measured')
                current_val = first_stage.get('current_measured')
                resistance_val = first_stage.get('resistance_measured')
            
            # PCB ID
            pcb_id: str = str(result.get('pcb_serial_number', 'N/A'))
            ctk.CTkLabel(result_frame, text=pcb_id, width=100).pack(side="left", padx=5)
            
            # Tester
            tester_id: str = str(result.get('user_id', 'N/A'))
            ctk.CTkLabel(result_frame, text=tester_id, width=100).pack(side="left", padx=5)
            
            # Status
            status: str = str(result.get('status', 'N/A'))
            status_color = "green" if status == "Pass" else "red"
            ctk.CTkLabel(
                result_frame,
                text=status,
                width=80,
                text_color=status_color,
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=5)
            
            # Voltage
            voltage_str = f"{voltage_val:.2f}V" if voltage_val is not None else "N/A"
            ctk.CTkLabel(result_frame, text=voltage_str, width=80).pack(side="left", padx=5)
            
            # Current
            current_str = f"{current_val:.2f}A" if current_val is not None else "N/A"
            ctk.CTkLabel(result_frame, text=current_str, width=80).pack(side="left", padx=5)
            
            # Resistance
            resistance_str = f"{resistance_val:.2f}Ω" if resistance_val is not None else "N/A"
            ctk.CTkLabel(result_frame, text=resistance_str, width=100).pack(side="left", padx=5)
            
            # Date/Time
            date_time: str = str(result.get('start_time', 'N/A'))
            ctk.CTkLabel(result_frame, text=date_time, width=150).pack(side="left", padx=5)
            
            # View details button
            view_btn = ctk.CTkButton(
                result_frame,
                text="View",
                width=80,
                command=lambda r=result: self.view_details(r)
            )
            view_btn.pack(side="left", padx=5)
    
    def view_details(self, result: DBRecord) -> None:
        """Show detailed view of a test result"""
        details_window: ctk.CTkToplevel = ctk.CTkToplevel(self)
        details_window.title("Test Result Details")
        details_window.geometry("500x600")
        
        # Make window appear on top
        details_window.attributes('-topmost', True)
        details_window.lift()
        details_window.focus_force()
        details_window.grab_set()
        
        # Center window
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - 250
        y = (details_window.winfo_screenheight() // 2) - 300
        details_window.geometry(f'500x600+{x}+{y}')
        
        container = ctk.CTkFrame(details_window)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="Test Result Details",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        # Get stage results to display measurements
        stage_results = self.db.get_stage_results(result['id'])
        
        # Build details text
        details_text = f"PCB ID: {result['pcb_serial_number']}\n"
        details_text += f"Tester: {result.get('user_id', 'Unknown')}\n"
        details_text += f"Status: {result['status']}\n\n"
        
        details_text += "Test Parameters:\n"
        
        # Get average/first stage measurements if available
        if stage_results and len(stage_results) > 0:
            # Get first stage result for display
            first_stage = stage_results[0]
            voltage = first_stage.get('voltage_measured')
            current = first_stage.get('current_measured')
            resistance = first_stage.get('resistance_measured')
            
            # Format with proper defaults
            voltage_str = f"{voltage:.2f}V" if voltage is not None else "N/A"
            current_str = f"{current:.2f}A" if current is not None else "N/A"
            resistance_str = f"{resistance:.2f}Ω" if resistance is not None else "N/A"
            
            details_text += f"  Voltage: {voltage_str}\n"
            details_text += f"  Current: {current_str}\n"
            details_text += f"  Resistance: {resistance_str}\n"
            
            # Add individual stage details if multiple stages
            if len(stage_results) > 1:
                details_text += "\nStage Details:\n"
                for idx, stage_result in enumerate(stage_results, 1):
                    v = stage_result.get('voltage_measured')
                    c = stage_result.get('current_measured')
                    r = stage_result.get('resistance_measured')
                    v_str = f"{v:.2f}" if v is not None else "N/A"
                    c_str = f"{c:.2f}" if c is not None else "N/A"
                    r_str = f"{r:.2f}" if r is not None else "N/A"
                    
                    details_text += f"  Stage {idx}:\n"
                    details_text += f"    Voltage: {v_str} V\n"
                    details_text += f"    Current: {c_str} A\n"
                    details_text += f"    Resistance: {r_str} Ω\n"
                    details_text += f"    Status: {stage_result.get('status', 'N/A')}\n"
        else:
            details_text += "  Voltage: N/A\n"
            details_text += "  Current: N/A\n"
            details_text += "  Resistance: N/A\n"
        
        details_text += f"\nNotes: {result.get('notes', 'N/A')}\n\n"
        details_text += f"Test Date/Time: {result.get('start_time', 'N/A')}"
        
        text_widget = ctk.CTkTextbox(container, width=450, height=400)
        text_widget.pack(pady=20)
        text_widget.insert("1.0", details_text)
        text_widget.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            container,
            text="Close",
            width=150,
            command=details_window.destroy
        )
        close_btn.pack(pady=10)
    
    def export_to_csv(self) -> None:
        """Export results to CSV file"""
        # Get current filtered results
        results: List[DBRecord] = self.db.get_test_results()
        if self.role == "tester":
            user_id: Any = self.db.get_user_id(self.username)
            results = [r for r in results if r.get('user_id') == user_id]
        status_filter: str = self.status_filter.get()
        if status_filter != "All":
            results = [r for r in results if r['status'] == status_filter]
        
        if not results:
            messagebox.showwarning("No Data", "No results to export")
            return
        
        # Ask for save location
        filename: str = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Test ID', 'PCB ID', 'Tester ID', 'Status', 'Voltage (V)', 'Current (A)', 'Resistance (Ω)', 'Notes', 'Test Date/Time'])
                
                # Write each result with measured values
                for result in results:
                    # Get stage results for measured values
                    stage_results = self.db.get_stage_results(result['id'])
                    voltage_val = "N/A"
                    current_val = "N/A"
                    resistance_val = "N/A"
                    
                    if stage_results and len(stage_results) > 0:
                        first_stage = stage_results[0]
                        v = first_stage.get('voltage_measured')
                        c = first_stage.get('current_measured')
                        r = first_stage.get('resistance_measured')
                        voltage_val = f"{v:.2f}" if v is not None else "N/A"
                        current_val = f"{c:.2f}" if c is not None else "N/A"
                        resistance_val = f"{r:.2f}" if r is not None else "N/A"
                    
                    writer.writerow([
                        result['id'],
                        result.get('pcb_serial_number', 'N/A'),
                        result.get('user_id', 'N/A'),
                        result.get('status', 'N/A'),
                        voltage_val,
                        current_val,
                        resistance_val,
                        result.get('notes', ''),
                        result.get('start_time', 'N/A')
                    ])
            
            messagebox.showinfo("Success", f"Results exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

"""
Results History Window
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from data.database import Database
import csv
from datetime import datetime

class ResultsHistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.db = Database()
        
        self.title("Test Results History")
        self.geometry("1200x700")
        
        self.center_window()
        self.create_widgets()
        self.load_results()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
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
    
    def load_results(self, *args):
        """Load and display test results"""
        # Clear existing
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        
        # Get filters
        status_filter = self.status_filter.get()
        search_query = self.search_entry.get().strip()
        
        # Get results based on role
        if self.role == "tester":
            results = self.db.get_test_results(username=self.username)
        else:
            results = self.db.get_test_results()
        
        # Apply filters
        if status_filter != "All":
            results = [r for r in results if r[3] == status_filter]
        
        if search_query:
            results = [r for r in results if search_query.lower() in r[1].lower()]
        
        # Update stats
        total = len(results)
        passed = len([r for r in results if r[3] == "PASS"])
        failed = len([r for r in results if r[3] == "FAIL"])
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
            
            # PCB ID
            ctk.CTkLabel(result_frame, text=result[1], width=100).pack(side="left", padx=5)
            
            # Tester
            ctk.CTkLabel(result_frame, text=result[2], width=100).pack(side="left", padx=5)
            
            # Status
            status_color = "green" if result[3] == "PASS" else "red"
            ctk.CTkLabel(
                result_frame,
                text=result[3],
                width=80,
                text_color=status_color,
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left", padx=5)
            
            # Voltage
            ctk.CTkLabel(result_frame, text=f"{result[4]:.2f}V", width=80).pack(side="left", padx=5)
            
            # Current
            ctk.CTkLabel(result_frame, text=f"{result[5]:.2f}A", width=80).pack(side="left", padx=5)
            
            # Resistance
            ctk.CTkLabel(result_frame, text=f"{result[6]:.1f}Ω", width=100).pack(side="left", padx=5)
            
            # Date/Time
            ctk.CTkLabel(result_frame, text=result[8], width=150).pack(side="left", padx=5)
            
            # View details button
            view_btn = ctk.CTkButton(
                result_frame,
                text="View",
                width=80,
                command=lambda r=result: self.view_details(r)
            )
            view_btn.pack(side="left", padx=5)
    
    def view_details(self, result):
        """Show detailed view of a test result"""
        details_window = ctk.CTkToplevel(self)
        details_window.title("Test Result Details")
        details_window.geometry("500x600")
        
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
        
        details_text = f"""
PCB ID: {result[1]}
Tester: {result[2]}
Status: {result[3]}

Test Parameters:
  Voltage: {result[4]:.2f} V
  Current: {result[5]:.2f} A
  Resistance: {result[6]:.1f} Ω

Notes: {result[7] if result[7] else 'N/A'}

Test Date/Time: {result[8]}
        """
        
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
    
    def export_to_csv(self):
        """Export results to CSV file"""
        # Get current filtered results
        if self.role == "tester":
            results = self.db.get_test_results(username=self.username)
        else:
            results = self.db.get_test_results()
        
        status_filter = self.status_filter.get()
        if status_filter != "All":
            results = [r for r in results if r[3] == status_filter]
        
        if not results:
            messagebox.showwarning("No Data", "No results to export")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['ID', 'PCB ID', 'Tester', 'Status', 'Voltage (V)', 'Current (A)', 'Resistance (Ω)', 'Notes', 'Date/Time'])
                writer.writerows(results)
            
            messagebox.showinfo("Success", f"Results exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

"""
Main Dashboard
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
import os
from typing import Union, Dict, Any, List
from config.config import DASHBOARD_WINDOW_SIZE, WINDOW_TITLE, LOGO_PATH, ROLE_ADMIN, ROLE_MANAGER, ROLE_TESTER
from data.database import Database, DBRecord
from ui.start_test import StartTestWindow
from ui.test_case_editor import TestCaseEditorWindow
from ui.results_history import ResultsHistoryWindow
from ui.stage_builder import StageBuilderWindow
from ui.advanced_test import AdvancedTestWindow
from ui.jig_diagram_viewer import JigDiagramViewerWindow
from ui.communication_config import CommunicationConfigWindow

class Dashboard(ctk.CTkToplevel):
    def __init__(self, username: str, role: Union[str, Dict[str, Any]], parent) -> None:
        super().__init__(parent)
        
        self.username: str = username
        # Ensure role is a string (handle both dict and string)
        self.role: str = self._extract_role(role)
        self.parent = parent
        self.db: Database = Database()
        
        self.title(f"{WINDOW_TITLE} - Dashboard")
        self.geometry(DASHBOARD_WINDOW_SIZE)
        
        # Center window
        self.center_window()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create UI
        self.create_widgets()
    
    def _extract_role(self, role: Union[str, Dict[str, Any]]) -> str:
        """Extract role string from either dict or string"""
        if isinstance(role, dict):
            extracted: Any = role.get('role')
            return extracted if isinstance(extracted, str) else ROLE_TESTER
        elif isinstance(role, str):
            return role
        else:
            return ROLE_TESTER
    
    def center_window(self) -> None:
        """Center the window on screen"""
        self.update_idletasks()
        width: int = 1200
        height: int = 700
        x: int = (self.winfo_screenwidth() // 2) - (width // 2)
        y: int = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self) -> None:
        """Create dashboard UI with modern drawer-based navigation"""
        # Top header with user info
        header_frame = ctk.CTkFrame(self, fg_color="#2B5A8C", corner_radius=0)
        header_frame.pack(side="top", fill="x", padx=0, pady=0)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"{WINDOW_TITLE} v2.0",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        header_label.pack(side="left", padx=20, pady=10)
        
        user_info = ctk.CTkLabel(
            header_frame,
            text=f"User: {self.username} | Role: {self.role.upper()}",
            font=ctk.CTkFont(size=11),
            text_color="white"
        )
        user_info.pack(side="right", padx=20, pady=10)
        
        # Main container
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True)
        
        # Left sidebar with icons/buttons
        self.sidebar = ctk.CTkFrame(main_container, width=80, fg_color="#3D3D3D", corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # Icon buttons for navigation
        self._create_sidebar_buttons()
        
        # Main content area
        self.main_content = ctk.CTkFrame(main_container, fg_color="#2A2A2A")
        self.main_content.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        
        # Store current view for cleanup
        self.current_view: Any = None
        self.show_dashboard()
    
    def _create_sidebar_buttons(self) -> None:
        """Create sidebar navigation buttons"""
        buttons_config = [
            ("Dashboard", "🏠", self.show_dashboard),
            ("Single Test", "▶", self.open_start_test),
            ("Batch Test", "⚙", self.open_advanced_test),
            ("Reports", "📊", self.open_results_history),
            ("Test Config", "⚙", self.open_test_case_editor),
        ]
        
        for label, icon, command in buttons_config:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{icon}\n{label}",
                width=70,
                height=70,
                command=command,
                font=ctk.CTkFont(size=9),
                corner_radius=5
            )
            btn.pack(pady=8, padx=5)
        
        # Add separator
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color="gray30")
        sep.pack(pady=10, padx=5, fill="x")
        
        # Stage Builder
        if self.role in [ROLE_ADMIN, ROLE_MANAGER]:
            btn = ctk.CTkButton(
                self.sidebar,
                text="🔧\nStage\nBuilder",
                width=70,
                height=70,
                command=self.open_stage_builder,
                font=ctk.CTkFont(size=9),
                corner_radius=5
            )
            btn.pack(pady=8, padx=5)
        
        # Communication Config
        if self.role == ROLE_ADMIN:
            btn = ctk.CTkButton(
                self.sidebar,
                text="📡\nComm\nConfig",
                width=70,
                height=70,
                command=self.open_comm_config,
                font=ctk.CTkFont(size=9),
                corner_radius=5
            )
            btn.pack(pady=8, padx=5)
        
        # Jig Diagram Viewer
        btn = ctk.CTkButton(
            self.sidebar,
            text="📐\nJig\nDiagram",
            width=70,
            height=70,
            command=self.open_jig_viewer,
            font=ctk.CTkFont(size=9),
            corner_radius=5
        )
        btn.pack(pady=8, padx=5)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪\nLogout",
            width=70,
            height=70,
            fg_color="red",
            hover_color="darkred",
            command=self.logout,
            font=ctk.CTkFont(size=9),
            corner_radius=5
        )
        logout_btn.pack(side="bottom", pady=8, padx=5)
    
    def show_dashboard(self) -> None:
        """Show dashboard welcome view with statistics and charts"""
        if self.current_view:
            self.current_view.pack_forget()
        
        self.current_view = ctk.CTkFrame(self.main_content)
        self.current_view.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title section
        title_section = ctk.CTkFrame(self.current_view, fg_color="transparent")
        title_section.pack(fill="x", pady=(0, 20))
        
        welcome_label = ctk.CTkLabel(
            title_section,
            text=f"Welcome, {self.username}!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        welcome_label.pack(side="left", padx=10)
        
        info_label = ctk.CTkLabel(
            title_section,
            text="PCB Testing Automation System - Phase 1",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        info_label.pack(side="left", padx=10)
        
        # Main content: Recent Batches and Analytics
        content_container = ctk.CTkFrame(self.current_view, fg_color="transparent")
        content_container.pack(fill="both", expand=True)
        
        # Left side - Recent Batches and Errors
        left_panel = ctk.CTkFrame(content_container, fg_color="#2A2A2A", corner_radius=10)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(
            left_panel,
            text="Recent Batches Summary",
            font=ctk.CTkFont(size=13, weight="bold")
        ).pack(pady=15, padx=15, anchor="w")
        
        # Get recent batches (simulated data - using test results)
        batches_data = self._get_recent_batches()
        batches_frame = ctk.CTkScrollableFrame(left_panel, fg_color="#2A2A2A")
        batches_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        for batch in batches_data[:5]:
            batch_item = ctk.CTkFrame(batches_frame, fg_color="#3D3D3D", corner_radius=8)
            batch_item.pack(fill="x", pady=5)
            
            batch_label = ctk.CTkLabel(
                batch_item,
                text=f"Batch #{batch['id']}: {batch['yield']}% Yield",
                font=ctk.CTkFont(size=11),
                text_color="lightgreen"
            )
            batch_label.pack(pady=10, padx=10, anchor="w")
        
        # Separator
        sep = ctk.CTkFrame(left_panel, height=1, fg_color="gray30")
        sep.pack(pady=10, padx=15, fill="x")
        
        # Recent Errors section
        ctk.CTkLabel(
            left_panel,
            text="Recent Errors",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FF6B6B"
        ).pack(pady=(15, 0), padx=15, anchor="w")
        
        errors_data = self._get_recent_errors()
        errors_frame = ctk.CTkScrollableFrame(left_panel, fg_color="#2A2A2A")
        errors_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))
        
        if errors_data:
            for error in errors_data[:5]:
                error_item = ctk.CTkFrame(errors_frame, fg_color="#3D3D3D", corner_radius=8)
                error_item.pack(fill="x", pady=3)
                
                error_label = ctk.CTkLabel(
                    error_item,
                    text=error.get('error_code', 'Unknown Error'),
                    font=ctk.CTkFont(size=10),
                    text_color="#FF9999"
                )
                error_label.pack(pady=5, padx=10, anchor="w")
        else:
            ctk.CTkLabel(
                errors_frame,
                text="No errors detected",
                font=ctk.CTkFont(size=11),
                text_color="lightgreen"
            ).pack(pady=20)
        
        # Right side - Statistics and Charts
        right_panel = ctk.CTkFrame(content_container, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Statistics cards
        stats_data = self._get_test_statistics()
        
        # Row 1: Test Status and Pass Rate
        stats_row1 = ctk.CTkFrame(right_panel, fg_color="transparent")
        stats_row1.pack(fill="x", pady=(0, 10))
        
        # Test Status Overview card
        status_card = ctk.CTkFrame(stats_row1, fg_color="#2A2A2A", corner_radius=10)
        status_card.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(
            status_card,
            text="Test Status Overview",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(15, 10), padx=15, anchor="w")
        
        self._draw_pie_chart(status_card, stats_data)
        
        # Pass Rate card
        passrate_card = ctk.CTkFrame(stats_row1, fg_color="#2A2A2A", corner_radius=10)
        passrate_card.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        ctk.CTkLabel(
            passrate_card,
            text="Overall Pass Rate",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(15, 20), padx=15, anchor="w")
        
        pass_rate: int = stats_data['pass_rate']
        rate_label = ctk.CTkLabel(
            passrate_card,
            text=f"{pass_rate}%",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="lightgreen" if pass_rate >= 80 else "orange" if pass_rate >= 60 else "red"
        )
        rate_label.pack(pady=(10, 20))
        
        total_tests: int = stats_data['total_tests']
        passed_tests: int = stats_data['passed_tests']
        ctk.CTkLabel(
            passrate_card,
            text=f"{passed_tests}/{total_tests} Tests Passed",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(0, 15), padx=15, anchor="w")
        
        # Row 2: Key Metrics
        stats_row2 = ctk.CTkFrame(right_panel, fg_color="transparent")
        stats_row2.pack(fill="x", pady=(0, 10))
        
        metrics = [
            ("Total Tests", str(stats_data['total_tests']), "lightblue"),
            ("Passed", str(stats_data['passed_tests']), "lightgreen"),
            ("Failed", str(stats_data['failed_tests']), "#FF9999"),
        ]
        
        for metric_name, metric_value, color in metrics:
            metric_card = ctk.CTkFrame(stats_row2, fg_color="#2A2A2A", corner_radius=8)
            metric_card.pack(side="left", fill="both", expand=True, padx=3)
            
            ctk.CTkLabel(
                metric_card,
                text=metric_name,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            ).pack(pady=(10, 5), padx=10)
            
            ctk.CTkLabel(
                metric_card,
                text=metric_value,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            ).pack(pady=(0, 10), padx=10)
    
    def _get_test_statistics(self) -> Dict[str, Any]:
        """Get test statistics from database"""
        try:
            results: List[DBRecord] = self.db.get_test_results()
            total: int = len(results)
            passed: int = sum(1 for r in results if r.get('overall_pass') or r.get('status') == 'PASS')
            failed: int = total - passed
            pass_rate: int = int((passed / total * 100) if total > 0 else 0)
            
            return {
                'total_tests': total,
                'passed_tests': passed,
                'failed_tests': failed,
                'pass_rate': pass_rate,
                'test_status': {
                    'passed': passed,
                    'failed': failed,
                    'not_run': 0
                }
            }
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_tests': 0,
                'passed_tests': 0,
                'failed_tests': 0,
                'pass_rate': 0,
                'test_status': {'passed': 0, 'failed': 0, 'not_run': 0}
            }
    
    def _get_recent_batches(self) -> List[Dict[str, Any]]:
        """Get recent batch data"""
        try:
            results: List[DBRecord] = self.db.get_test_results()
            batches: Dict[int, Dict[str, Any]] = {}
            
            for result in results:
                batch_id: int = int(result.get('id', 0))
                passed: bool = result.get('overall_pass', False) or result.get('status') == 'PASS'
                
                if batch_id not in batches:
                    batches[batch_id] = {'id': batch_id, 'total': 0, 'passed': 0}
                
                batches[batch_id]['total'] += 1
                if passed:
                    batches[batch_id]['passed'] += 1
            
            batch_list = []
            for batch_id in sorted(batches.keys(), reverse=True):
                batch = batches[batch_id]
                yield_pct: int = int((batch['passed'] / batch['total'] * 100) if batch['total'] > 0 else 0)
                batch_list.append({'id': batch_id, 'yield': yield_pct})
            
            return batch_list
        except Exception as e:
            print(f"Error getting batches: {e}")
            return [{'id': i, 'yield': 100} for i in range(1, 6)]
    
    def _get_recent_errors(self) -> List[Dict[str, Any]]:
        """Get recent errors from test results"""
        try:
            results: List[DBRecord] = self.db.get_test_results()
            errors = []
            
            for result in results:
                notes: str = result.get('notes', '')
                if notes and notes.lower() != 'pass':
                    errors.append({
                        'error_code': notes[:30],
                        'test_id': result.get('id')
                    })
            
            return errors[:5]
        except Exception as e:
            print(f"Error getting errors: {e}")
            return []
    
    def _draw_pie_chart(self, parent: ctk.CTkFrame, stats: Dict[str, Any]) -> None:
        """Draw a pie chart showing test status distribution"""
        try:
            # Create pie chart image
            size: int = 150
            image = Image.new('RGB', (size, size), color='#2A2A2A')
            draw = ImageDraw.Draw(image)
            
            test_status = stats['test_status']
            passed = test_status['passed']
            failed = test_status['failed']
            total = passed + failed
            
            if total == 0:
                # Draw empty pie chart
                draw.ellipse([5, 5, size-5, size-5], fill='#555555', outline='#888888')
            else:
                # Draw pie slices
                passed_angle = (passed / total) * 360
                failed_angle = (failed / total) * 360
                
                # Passed slice (green)
                draw.pieslice([5, 5, size-5, size-5], 0, int(passed_angle), fill='#00DD00', outline='#333333')
                
                # Failed slice (red)
                draw.pieslice([5, 5, size-5, size-5], int(passed_angle), 360, fill='#DD0000', outline='#333333')
            
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
            chart_label = ctk.CTkLabel(parent, image=photo, text="")
            chart_label.image = photo
            chart_label.pack(pady=10)
            
            # Legend
            legend_frame = ctk.CTkFrame(parent, fg_color="transparent")
            legend_frame.pack(pady=10, padx=15, fill="x")
            
            legend_items = [
                ("Pass", "lightgreen"),
                ("Fail", "#FF6B6B"),
            ]
            
            for label, color in legend_items:
                item = ctk.CTkFrame(legend_frame, fg_color="transparent")
                item.pack(side="left", padx=10)
                
                indicator = ctk.CTkLabel(
                    item,
                    text="●",
                    font=ctk.CTkFont(size=12),
                    text_color=color
                )
                indicator.pack(side="left", padx=(0, 5))
                
                ctk.CTkLabel(
                    item,
                    text=label,
                    font=ctk.CTkFont(size=10)
                ).pack(side="left")
        except Exception as e:
            print(f"Error drawing pie chart: {e}")
            ctk.CTkLabel(
                parent,
                text="Chart unavailable",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(pady=20)
    
    def open_start_test(self) -> None:
        """Load Start Test view"""
        self._switch_view(StartTestWindow(self.main_content, self.username, is_embedded=True))
    
    def open_results_history(self) -> None:
        """Load Results History view"""
        self._switch_view(ResultsHistoryWindow(self.main_content, self.username, self.role, is_embedded=True))
    
    def open_test_case_editor(self) -> None:
        """Load Test Case Editor view"""
        self._switch_view(TestCaseEditorWindow(self.main_content, self.username, self.role, is_embedded=True))
    
    def open_stage_builder(self) -> None:
        """Load Stage Builder view"""
        self._switch_view(StageBuilderWindow(self.main_content, self.username, self.role, is_embedded=True))
    
    def open_advanced_test(self) -> None:
        """Load Advanced Test view"""
        self._switch_view(AdvancedTestWindow(self.main_content, self.username, is_embedded=True))
    
    def open_jig_viewer(self) -> None:
        """Load Jig Diagram Viewer view"""
        self._switch_view(JigDiagramViewerWindow(self.main_content, self.username, self.role, is_embedded=True))
    
    def open_comm_config(self) -> None:
        """Load Communication Config view"""
        self._switch_view(CommunicationConfigWindow(self.main_content, self.username, self.role, is_embedded=True))
    
    def _switch_view(self, new_view: Any) -> None:
        """Switch to a new view, clearing the old one"""
        if self.current_view:
            self.current_view.pack_forget()
        self.current_view = new_view
        self.current_view.pack(fill="both", expand=True)
    
    def coming_soon(self) -> None:
        """Placeholder for features coming in later phases"""
        messagebox.showinfo("Coming Soon", "This feature will be available in the next phase")
    
    def logout(self) -> None:
        """Logout and return to login screen"""
        self.destroy()
        self.parent.deiconify()
        self.parent.username_entry.delete(0, 'end')
        self.parent.password_entry.delete(0, 'end')
    
    def on_closing(self) -> None:
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Do you want to logout?"):
            self.logout()

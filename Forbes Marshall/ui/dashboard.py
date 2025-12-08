"""
Main Dashboard
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from config.config import DASHBOARD_WINDOW_SIZE, WINDOW_TITLE, LOGO_PATH, ROLE_ADMIN, ROLE_MANAGER, ROLE_TESTER
from ui.start_test import StartTestWindow
from ui.test_case_editor import TestCaseEditorWindow
from ui.results_history import ResultsHistoryWindow
from ui.stage_builder import StageBuilderWindow
from ui.advanced_test import AdvancedTestWindow
from ui.jig_diagram_viewer import JigDiagramViewerWindow
from ui.communication_config import CommunicationConfigWindow

class Dashboard(ctk.CTkToplevel):
    def __init__(self, username, role, parent):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.parent = parent
        
        self.title(f"{WINDOW_TITLE} - Dashboard")
        self.geometry(DASHBOARD_WINDOW_SIZE)
        
        # Center window
        self.center_window()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create UI
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create dashboard UI"""
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo in sidebar
        if os.path.exists(LOGO_PATH):
            try:
                logo_image = Image.open(LOGO_PATH)
                logo_image = logo_image.resize((200, 67), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(200, 67))
                logo_label = ctk.CTkLabel(self.sidebar, image=logo_photo, text="")
                logo_label.pack(pady=(20, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar)
        user_frame.pack(pady=20, padx=10, fill="x")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"User: {self.username}",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        user_label.pack(pady=5)
        
        role_label = ctk.CTkLabel(
            user_frame,
            text=f"Role: {self.role.upper()}",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        role_label.pack(pady=5)
        
        # Menu buttons
        ctk.CTkLabel(
            self.sidebar,
            text="MENU",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(20, 10))
        
        # Start Test - Available to all
        self.start_test_btn = ctk.CTkButton(
            self.sidebar,
            text="Start Test",
            width=220,
            height=40,
            command=self.open_start_test
        )
        self.start_test_btn.pack(pady=10, padx=15)
        
        # Results History - Available to all
        self.results_btn = ctk.CTkButton(
            self.sidebar,
            text="Results History",
            width=220,
            height=40,
            command=self.open_results_history
        )
        self.results_btn.pack(pady=10, padx=15)
        
        # Stage Builder - Manager+
        if self.role in [ROLE_ADMIN, ROLE_MANAGER]:
            self.stage_builder_btn = ctk.CTkButton(
                self.sidebar,
                text="Stage Builder",
                width=220,
                height=40,
                command=self.open_stage_builder
            )
            self.stage_builder_btn.pack(pady=10, padx=15)
        
        # Advanced Test - Available to all
        self.advanced_test_btn = ctk.CTkButton(
            self.sidebar,
            text="Advanced Test",
            width=220,
            height=40,
            command=self.open_advanced_test
        )
        self.advanced_test_btn.pack(pady=10, padx=15)
        
        # Communication Config - Admin only
        if self.role == ROLE_ADMIN:
            self.comm_config_btn = ctk.CTkButton(
                self.sidebar,
                text="Communication Config",
                width=220,
                height=40,
                command=self.open_comm_config
            )
            self.comm_config_btn.pack(pady=10, padx=15)
        
        # Test Case Editor - Manager+
        if self.role in [ROLE_ADMIN, ROLE_MANAGER]:
            self.test_editor_btn = ctk.CTkButton(
                self.sidebar,
                text="Test Case Editor",
                width=220,
                height=40,
                command=self.open_test_case_editor
            )
            self.test_editor_btn.pack(pady=10, padx=15)
        
        # Jig Diagram Viewer - All
        self.jig_viewer_btn = ctk.CTkButton(
            self.sidebar,
            text="Jig Diagram Viewer",
            width=220,
            height=40,
            command=self.open_jig_viewer
        )
        self.jig_viewer_btn.pack(pady=10, padx=15)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            width=220,
            height=40,
            fg_color="red",
            hover_color="darkred",
            command=self.logout
        )
        logout_btn.pack(side="bottom", pady=20, padx=15)
        
        # Main content area
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.main_content,
            text=f"Welcome, {self.username}!",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        welcome_label.pack(pady=(50, 20))
        
        info_label = ctk.CTkLabel(
            self.main_content,
            text="PCB Testing Automation System - Phase 1",
            font=ctk.CTkFont(size=16)
        )
        info_label.pack(pady=10)
        
        # Quick stats frame
        stats_frame = ctk.CTkFrame(self.main_content)
        stats_frame.pack(pady=40, padx=50, fill="x")
        
        ctk.CTkLabel(
            stats_frame,
            text="Quick Start",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=20)
        
        ctk.CTkLabel(
            stats_frame,
            text="Click 'Start Test' to begin PCB testing",
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)
    
    def open_start_test(self):
        """Open Start Test window"""
        StartTestWindow(self, self.username)
    
    def open_results_history(self):
        """Open Results History window"""
        ResultsHistoryWindow(self, self.username, self.role)
    
    def open_test_case_editor(self):
        """Open Test Case Editor window"""
        TestCaseEditorWindow(self, self.username, self.role)
    
    def open_stage_builder(self):
        """Open Stage Builder window"""
        StageBuilderWindow(self, self.username, self.role)
    
    def open_advanced_test(self):
        """Open Advanced Test window"""
        AdvancedTestWindow(self, self.username)
    
    def open_jig_viewer(self):
        """Open Jig Diagram Viewer window"""
        JigDiagramViewerWindow(self, self.username, self.role)
    
    def open_comm_config(self):
        """Open Communication Config window"""
        CommunicationConfigWindow(self, self.username, self.role)
    
    def coming_soon(self):
        """Placeholder for features coming in later phases"""
        messagebox.showinfo("Coming Soon", "This feature will be available in the next phase")
    
    def logout(self):
        """Logout and return to login screen"""
        self.destroy()
        self.parent.deiconify()
        self.parent.username_entry.delete(0, 'end')
        self.parent.password_entry.delete(0, 'end')
    
    def on_closing(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Do you want to logout?"):
            self.logout()

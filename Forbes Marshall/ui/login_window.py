"""
Login Window
"""
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
from data.database import Database
from ui.dashboard import Dashboard
from config.config import LOGIN_WINDOW_SIZE, WINDOW_TITLE, LOGO_PATH

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(WINDOW_TITLE)
        self.geometry(LOGIN_WINDOW_SIZE)
        self.resizable(False, False)
        
        self.db = Database()
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_widgets()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create login UI widgets"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo
        if os.path.exists(LOGO_PATH):
            try:
                logo_image = Image.open(LOGO_PATH)
                logo_image = logo_image.resize((300, 100), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(300, 100))
                logo_label = ctk.CTkLabel(container, image=logo_photo, text="")
                logo_label.pack(pady=(20, 10))
            except Exception as e:
                print(f"Error loading logo: {e}")
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="PCB Testing System",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 30))
        
        # Username
        username_label = ctk.CTkLabel(container, text="Username", font=ctk.CTkFont(size=12))
        username_label.pack(pady=(10, 5))
        
        self.username_entry = ctk.CTkEntry(
            container,
            width=300,
            height=40,
            placeholder_text="Enter username"
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Password
        password_label = ctk.CTkLabel(container, text="Password", font=ctk.CTkFont(size=12))
        password_label.pack(pady=(10, 5))
        
        self.password_entry = ctk.CTkEntry(
            container,
            width=300,
            height=40,
            placeholder_text="Enter password",
            show="*"
        )
        self.password_entry.pack(pady=(0, 25))
        
        # Login button
        login_button = ctk.CTkButton(
            container,
            text="Login",
            width=300,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.login
        )
        login_button.pack(pady=(10, 10))
        
        # Info label
        info_label = ctk.CTkLabel(
            container,
            text="Default credentials:\nadmin/admin123, manager/manager123, tester/tester123",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info_label.pack(pady=(20, 10))
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        role = self.db.authenticate_user(username, password)
        
        if role:
            self.withdraw()
            dashboard = Dashboard(username, role, self)
            dashboard.mainloop()
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, 'end')

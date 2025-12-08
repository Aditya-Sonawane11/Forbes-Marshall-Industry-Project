"""
PCB Testing Automation System
Main Entry Point
"""
import customtkinter as ctk
from ui.login_window import LoginWindow

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    app = LoginWindow()
    app.mainloop()

if __name__ == "__main__":
    main()

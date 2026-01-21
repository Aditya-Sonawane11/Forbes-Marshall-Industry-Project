"""
PCB Testing Automation System
Main Entry Point
"""
import customtkinter as ctk
from ui.login_window import LoginWindow
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Print to terminal
        logging.FileHandler('pcb_testing.log')  # Also save to file
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("PCB Testing System Started")
    logger.info("=" * 80)
    
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    logger.info("Initializing Login Window")
    app = LoginWindow()
    logger.info("Login Window created, starting mainloop")
    app.mainloop()
    logger.info("Application closed")

if __name__ == "__main__":
    main()

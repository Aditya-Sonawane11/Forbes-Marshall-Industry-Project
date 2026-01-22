"""
Jig Diagram Viewer Window
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import logging
from data.database import Database, DBRecord
from typing import Optional, List

# Set up logger for this module
logger = logging.getLogger(__name__)

class JigDiagramViewerWindow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, username: str, role: str, is_embedded: bool = False) -> None:
        super().__init__(parent)
        
        self.username: str = username
        self.role: str = role
        self.db: Database = Database()
        self.current_diagram: Optional[DBRecord] = None
        self.current_image: Optional[ctk.CTkImage] = None
        self.diagrams_data: List[DBRecord] = []
        
        # Ensure diagrams directory exists
        os.makedirs("assets/diagrams", exist_ok=True)
        
        logger.info(f"Initializing JigDiagramViewerWindow for user: {username}")
        
        self.center_window()
        self.create_widgets()
        self.load_diagrams()
    
    def center_window(self) -> None:
        """Placeholder for compatibility"""
        pass
    
    def create_widgets(self) -> None:
        """Create jig diagram viewer UI"""
        # Main container
        container: ctk.CTkFrame = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Jig Diagram Viewer",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Top controls
        controls_frame = ctk.CTkFrame(container)
        controls_frame.pack(pady=10, padx=20, fill="x")
        
        # Diagram selection
        ctk.CTkLabel(controls_frame, text="Select Diagram:", font=ctk.CTkFont(size=14)).pack(side="left", padx=10)
        self.diagram_combo = ctk.CTkComboBox(
            controls_frame,
            values=["No diagrams available"],
            width=300,
            command=self.on_diagram_selected
        )
        self.diagram_combo.pack(side="left", padx=10)
        
        # Admin controls
        if self.role == "admin":
            upload_btn = ctk.CTkButton(
                controls_frame,
                text="Upload Diagram",
                width=150,
                command=self.upload_diagram
            )
            upload_btn.pack(side="right", padx=10)
        
        # Diagram info
        self.info_label = ctk.CTkLabel(
            container,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.info_label.pack(pady=5)
        
        # Image display area
        self.image_frame = ctk.CTkFrame(container)
        self.image_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Scrollable frame for image
        self.image_scroll = ctk.CTkScrollableFrame(self.image_frame)
        self.image_scroll.pack(fill="both", expand=True)
        
        self.image_label = ctk.CTkLabel(
            self.image_scroll,
            text="Select a diagram to view",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.image_label.pack(pady=50)
        
        # Bottom controls
        bottom_frame = ctk.CTkFrame(container)
        bottom_frame.pack(pady=10)
        
        if self.role == "admin" and self.current_diagram:
            delete_btn = ctk.CTkButton(
                bottom_frame,
                text="Delete Diagram",
                width=150,
                fg_color="red",
                hover_color="darkred",
                command=self.delete_diagram
            )
            delete_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(
            bottom_frame,
            text="Close",
            width=150,
            height=40,
            fg_color="gray",
            command=self.destroy
        )
        close_btn.pack(side="left", padx=10)
    
    def load_diagrams(self) -> None:
        """Load available diagrams"""
        diagrams: List[DBRecord] = self.db.get_jig_diagrams()
        
        if diagrams:
            diagram_names = [f"{diag['name']} - {diag.get('description', 'N/A')}" for diag in diagrams]
            self.diagram_combo.configure(values=diagram_names)
            self.diagrams_data = diagrams
        else:
            self.diagram_combo.configure(values=["No diagrams available"])
            self.diagrams_data = []
    
    def on_diagram_selected(self, choice: str) -> None:
        """Handle diagram selection"""
        if not self.diagrams_data or choice == "No diagrams available":
            return
        
        # Find selected diagram
        for diag in self.diagrams_data:
            if f"{diag['name']} - {diag.get('description', 'N/A')}" == choice:
                self.current_diagram = diag
                break
        
        if self.current_diagram:
            self.display_diagram()
    
    def display_diagram(self) -> None:
        """Display the selected diagram"""
        if not self.current_diagram:
            logger.warning("No diagram selected")
            return
        
        diagram_path: str = self.current_diagram.get('image_path', '')
        
        if not os.path.exists(diagram_path):
            logger.error(f"Diagram file not found: {diagram_path}")
            messagebox.showerror("Error", "Diagram file not found")
            return
        
        try:
            # Load and display image
            image: Image.Image = Image.open(diagram_path)
            logger.info(f"Loaded diagram: {diagram_path}, Size: {image.size}")
            
            # Resize to fit (max 800x500)
            max_width: int = 800
            max_height: int = 500
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            
            self.image_label.configure(image=photo, text="")
            self.current_image = photo  # Keep reference to prevent garbage collection
            
            # Update info
            name = self.current_diagram.get('name', 'N/A')
            description = self.current_diagram.get('description', 'N/A')
            self.info_label.configure(
                text=f"Diagram: {name} | Type: {description}"
            )
            logger.info(f"Displayed diagram: {name}")
            
        except Exception as e:
            logger.error(f"Failed to load diagram: {str(e)}")
            messagebox.showerror("Error", f"Failed to load diagram: {str(e)}")
    
    def upload_diagram(self) -> None:
        """Upload a new diagram (Admin only)"""
        # Ask for image file
        file_path: str = filedialog.askopenfilename(
            title="Select Jig Diagram Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Create upload dialog
        upload_dialog: ctk.CTkToplevel = ctk.CTkToplevel(self)
        upload_dialog.title("Upload Diagram")
        upload_dialog.geometry("400x300")
        
        # Make window appear on top
        upload_dialog.attributes('-topmost', True)
        upload_dialog.lift()
        upload_dialog.focus_force()
        upload_dialog.grab_set()
        
        # Center dialog
        upload_dialog.update_idletasks()
        x: int = (upload_dialog.winfo_screenwidth() // 2) - 200
        y: int = (upload_dialog.winfo_screenheight() // 2) - 150
        upload_dialog.geometry(f'400x300+{x}+{y}')
        
        container: ctk.CTkFrame = ctk.CTkFrame(upload_dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="Upload Jig Diagram",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Diagram name
        ctk.CTkLabel(container, text="Diagram Name:").pack(pady=5)
        name_entry: ctk.CTkEntry = ctk.CTkEntry(container, width=300, placeholder_text="e.g., Main Test Jig")
        name_entry.pack(pady=5)
        
        # PCB Type
        ctk.CTkLabel(container, text="PCB Type:").pack(pady=5)
        pcb_entry: ctk.CTkEntry = ctk.CTkEntry(container, width=300, placeholder_text="e.g., Power Board")
        pcb_entry.pack(pady=5)
        
        # Description
        ctk.CTkLabel(container, text="Description:").pack(pady=5)
        desc_entry: ctk.CTkEntry = ctk.CTkEntry(container, width=300, placeholder_text="Optional description")
        desc_entry.pack(pady=5)
        
        def save_diagram() -> None:
            name: str = name_entry.get().strip()
            pcb_type: str = pcb_entry.get().strip()
            description: str = desc_entry.get().strip()
            
            if not name or not pcb_type:
                logger.warning("Diagram upload: Missing name or PCB type")
                messagebox.showerror("Error", "Please enter diagram name and PCB type")
                return
            
            # Create diagrams directory if it doesn't exist
            diagrams_dir: str = "assets/diagrams"
            os.makedirs(diagrams_dir, exist_ok=True)
            
            # Copy file to diagrams directory
            import shutil
            filename: str = os.path.basename(file_path)
            dest_path: str = os.path.join(diagrams_dir, filename)
            
            try:
                shutil.copy2(file_path, dest_path)
                logger.info(f"Copied diagram file to: {dest_path}")
                
                # Get user_id for uploaded_by parameter
                user_id: Optional[int] = self.db.get_user_id(self.username)
                
                # Save to database with new signature
                diagram_id: Optional[int] = self.db.save_jig_diagram(
                    test_case_id=None,
                    diagram_name=name,
                    file_path=dest_path,
                    description=pcb_type,
                    uploaded_by=user_id
                )
                
                if diagram_id:
                    logger.info(f"Diagram saved with ID: {diagram_id}, Name: {name}")
                    messagebox.showinfo("Success", "Diagram uploaded successfully!")
                    upload_dialog.destroy()
                    self.load_diagrams()
                else:
                    logger.error("Failed to save diagram to database")
                    messagebox.showerror("Error", "Failed to save diagram")
            except Exception as e:
                logger.error(f"Failed to upload diagram: {str(e)}")
                messagebox.showerror("Error", f"Failed to upload diagram: {str(e)}")
                messagebox.showerror("Error", f"Failed to upload diagram: {str(e)}")
        
        save_btn = ctk.CTkButton(
            container,
            text="Save",
            width=150,
            command=save_diagram
        )
        save_btn.pack(pady=20)
    
    def delete_diagram(self) -> None:
        """Delete the current diagram (Admin only)"""
        if not self.current_diagram:
            logger.warning("No diagram selected for deletion")
            return
        
        diagram_name = self.current_diagram.get('name', 'Unknown')
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete '{diagram_name}'?"):
            # Delete file
            try:
                file_path = self.current_diagram.get('image_path', '')
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted diagram file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file: {e}")
            
            # Delete from database
            try:
                self.db.delete_jig_diagram(self.current_diagram['id'])
                logger.info(f"Deleted diagram from database: ID {self.current_diagram['id']}")
            except Exception as e:
                logger.error(f"Error deleting from database: {e}")
            
            self.current_diagram = None
            messagebox.showinfo("Success", "Diagram deleted")
            self.load_diagrams()
            self.image_label.configure(image=None, text="Select a diagram to view")
            self.info_label.configure(text="")
            self.load_diagrams()
            
            messagebox.showinfo("Success", "Diagram deleted")

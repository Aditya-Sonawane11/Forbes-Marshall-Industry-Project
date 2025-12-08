"""
Jig Diagram Viewer Window
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
from data.database import Database

class JigDiagramViewerWindow(ctk.CTkToplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.db = Database()
        self.current_diagram = None
        
        self.title("Jig Diagram Viewer")
        self.geometry("1000x750")
        
        self.center_window()
        self.create_widgets()
        self.load_diagrams()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 1000
        height = 750
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create jig diagram viewer UI"""
        # Main container
        container = ctk.CTkFrame(self)
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
    
    def load_diagrams(self):
        """Load available diagrams"""
        diagrams = self.db.get_jig_diagrams()
        
        if diagrams:
            diagram_names = [f"{diag[1]} - {diag[2]}" for diag in diagrams]
            self.diagram_combo.configure(values=diagram_names)
            self.diagrams_data = diagrams
        else:
            self.diagram_combo.configure(values=["No diagrams available"])
            self.diagrams_data = []
    
    def on_diagram_selected(self, choice):
        """Handle diagram selection"""
        if not self.diagrams_data or choice == "No diagrams available":
            return
        
        # Find selected diagram
        for diag in self.diagrams_data:
            if f"{diag[1]} - {diag[2]}" == choice:
                self.current_diagram = diag
                break
        
        if self.current_diagram:
            self.display_diagram()
    
    def display_diagram(self):
        """Display the selected diagram"""
        if not self.current_diagram:
            return
        
        diagram_path = self.current_diagram[3]
        
        if not os.path.exists(diagram_path):
            messagebox.showerror("Error", "Diagram file not found")
            return
        
        try:
            # Load and display image
            image = Image.open(diagram_path)
            
            # Resize to fit (max 800x500)
            max_width = 800
            max_height = 500
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            photo = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # Keep reference
            
            # Update info
            self.info_label.configure(
                text=f"PCB Type: {self.current_diagram[2]} | Description: {self.current_diagram[4] or 'N/A'}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load diagram: {str(e)}")
    
    def upload_diagram(self):
        """Upload a new diagram (Admin only)"""
        # Ask for image file
        file_path = filedialog.askopenfilename(
            title="Select Jig Diagram Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        # Create upload dialog
        upload_dialog = ctk.CTkToplevel(self)
        upload_dialog.title("Upload Diagram")
        upload_dialog.geometry("400x300")
        
        # Center dialog
        upload_dialog.update_idletasks()
        x = (upload_dialog.winfo_screenwidth() // 2) - 200
        y = (upload_dialog.winfo_screenheight() // 2) - 150
        upload_dialog.geometry(f'400x300+{x}+{y}')
        
        container = ctk.CTkFrame(upload_dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            container,
            text="Upload Jig Diagram",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Diagram name
        ctk.CTkLabel(container, text="Diagram Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(container, width=300, placeholder_text="e.g., Main Test Jig")
        name_entry.pack(pady=5)
        
        # PCB Type
        ctk.CTkLabel(container, text="PCB Type:").pack(pady=5)
        pcb_entry = ctk.CTkEntry(container, width=300, placeholder_text="e.g., Power Board")
        pcb_entry.pack(pady=5)
        
        # Description
        ctk.CTkLabel(container, text="Description:").pack(pady=5)
        desc_entry = ctk.CTkEntry(container, width=300, placeholder_text="Optional description")
        desc_entry.pack(pady=5)
        
        def save_diagram():
            name = name_entry.get().strip()
            pcb_type = pcb_entry.get().strip()
            description = desc_entry.get().strip()
            
            if not name or not pcb_type:
                messagebox.showerror("Error", "Please enter diagram name and PCB type")
                return
            
            # Create diagrams directory if it doesn't exist
            diagrams_dir = "assets/diagrams"
            os.makedirs(diagrams_dir, exist_ok=True)
            
            # Copy file to diagrams directory
            import shutil
            filename = os.path.basename(file_path)
            dest_path = os.path.join(diagrams_dir, filename)
            
            try:
                shutil.copy2(file_path, dest_path)
                
                # Save to database
                success = self.db.save_jig_diagram(name, pcb_type, dest_path, description, self.username)
                
                if success:
                    messagebox.showinfo("Success", "Diagram uploaded successfully!")
                    upload_dialog.destroy()
                    self.load_diagrams()
                else:
                    messagebox.showerror("Error", "Failed to save diagram")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload diagram: {str(e)}")
        
        save_btn = ctk.CTkButton(
            container,
            text="Save",
            width=150,
            command=save_diagram
        )
        save_btn.pack(pady=20)
    
    def delete_diagram(self):
        """Delete the current diagram (Admin only)"""
        if not self.current_diagram:
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this diagram?"):
            # Delete file
            try:
                if os.path.exists(self.current_diagram[3]):
                    os.remove(self.current_diagram[3])
            except Exception as e:
                print(f"Error deleting file: {e}")
            
            # Delete from database
            self.db.delete_jig_diagram(self.current_diagram[0])
            
            self.current_diagram = None
            self.image_label.configure(image=None, text="Select a diagram to view")
            self.info_label.configure(text="")
            self.load_diagrams()
            
            messagebox.showinfo("Success", "Diagram deleted")

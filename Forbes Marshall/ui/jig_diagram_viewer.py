"""
Jig Diagram Viewer Window
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import os
import logging
from datetime import datetime
from data.database import Database, DBRecord
from config.config import ROLE_ADMIN
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

        # Header with title and upload button
        header_frame = ctk.CTkFrame(container)
        header_frame.pack(pady=(10, 20), fill="x")

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Jig Diagram Manager",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", pady=10, padx=10)

        # Prominent upload button (Admin only)
        if self.role == ROLE_ADMIN:
            upload_btn = ctk.CTkButton(
                header_frame,
                text="📁 Upload New Diagram",
                width=180,
                height=40,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#28a745",
                hover_color="#218838",
                command=self.upload_diagram
            )
            upload_btn.pack(side="right", pady=10, padx=10)

        # Search and filter controls
        search_frame = ctk.CTkFrame(container)
        search_frame.pack(pady=10, padx=20, fill="x")

        # Search box
        ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(10, 5))
        self.search_entry = ctk.CTkEntry(
            search_frame,
            width=200,
            placeholder_text="Search by name or description..."
        )
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_changed)

        # Filter by PCB type
        ctk.CTkLabel(search_frame, text="📦 Filter by PCB Type:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(20, 5))
        self.pcb_filter_combo = ctk.CTkComboBox(
            search_frame,
            values=["All Types"],
            width=150,
            command=self.on_filter_changed
        )
        self.pcb_filter_combo.pack(side="left", padx=5)

        # Clear search button
        clear_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            width=80,
            height=28,
            command=self.clear_search
        )
        clear_btn.pack(side="left", padx=(10, 5))

        # Diagram count label
        self.count_label = ctk.CTkLabel(
            search_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.count_label.pack(side="right", padx=(5, 10))

        # Main content area (two panels)
        content_frame = ctk.CTkFrame(container)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Left panel - Diagram list
        left_panel = ctk.CTkFrame(content_frame)
        left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_panel.configure(width=350)

        ctk.CTkLabel(
            left_panel,
            text="📋 Available Diagrams",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Diagram list with custom cards
        self.diagrams_scroll = ctk.CTkScrollableFrame(left_panel, height=400)
        self.diagrams_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Bulk operations (Admin only)
        if self.role == ROLE_ADMIN:
            bulk_frame = ctk.CTkFrame(left_panel)
            bulk_frame.pack(fill="x", padx=10, pady=5)

            self.select_all_var = ctk.BooleanVar()
            select_all_cb = ctk.CTkCheckBox(
                bulk_frame,
                text="Select All",
                variable=self.select_all_var,
                command=self.toggle_select_all
            )
            select_all_cb.pack(side="left", padx=5, pady=5)

            bulk_delete_btn = ctk.CTkButton(
                bulk_frame,
                text="🗑️ Delete Selected",
                width=120,
                height=30,
                fg_color="#dc3545",
                hover_color="#c82333",
                command=self.bulk_delete_diagrams
            )
            bulk_delete_btn.pack(side="right", padx=5, pady=5)

        # Right panel - Diagram viewer
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        # Diagram info header
        info_header = ctk.CTkFrame(right_panel)
        info_header.pack(fill="x", padx=10, pady=10)

        self.diagram_title = ctk.CTkLabel(
            info_header,
            text="Select a diagram to view",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.diagram_title.pack(side="left", pady=5)

        # Diagram actions (when diagram selected)
        self.actions_frame = ctk.CTkFrame(info_header)
        self.actions_frame.pack(side="right", padx=10)
        self.actions_frame.pack_forget()  # Initially hidden

        # Image display area with enhanced controls
        self.image_frame = ctk.CTkFrame(right_panel)
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollable frame for image with zoom controls
        image_controls = ctk.CTkFrame(self.image_frame)
        image_controls.pack(fill="x", padx=5, pady=5)

        self.zoom_var = ctk.DoubleVar(value=1.0)
        ctk.CTkLabel(image_controls, text="🔍 Zoom:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)

        zoom_slider = ctk.CTkSlider(
            image_controls,
            from_=0.5,
            to=3.0,
            variable=self.zoom_var,
            width=150,
            command=self.on_zoom_changed
        )
        zoom_slider.pack(side="left", padx=5)

        self.zoom_label = ctk.CTkLabel(image_controls, text="100%", font=ctk.CTkFont(size=12))
        self.zoom_label.pack(side="left", padx=5)

        reset_zoom_btn = ctk.CTkButton(
            image_controls,
            text="Reset",
            width=60,
            height=25,
            command=self.reset_zoom
        )
        reset_zoom_btn.pack(side="left", padx=5)

        self.image_scroll = ctk.CTkScrollableFrame(self.image_frame)
        self.image_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.image_label = ctk.CTkLabel(
            self.image_scroll,
            text="📋 Select a diagram from the list to view it here",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.image_label.pack(pady=50)

        # Initialize selection tracking for bulk operations
        if self.role == ROLE_ADMIN:
            self.selected_diagrams = set()
            self.diagram_checkboxes = {}

        # Initialize original image for zoom
        self.original_image = None
    
    def load_diagrams(self) -> None:
        """Load available diagrams and populate the list"""
        diagrams: List[DBRecord] = self.db.get_jig_diagrams()
        self.diagrams_data = diagrams

        # Update PCB type filter options
        pcb_types = set()
        for diag in diagrams:
            pcb_type = diag.get('description', 'N/A')
            if pcb_type != 'N/A':
                pcb_types.add(pcb_type)

        filter_values = ["All Types"] + sorted(list(pcb_types))
        self.pcb_filter_combo.configure(values=filter_values)

        # Apply current filters and search
        self.filter_and_display_diagrams()

    def filter_and_display_diagrams(self) -> None:
        """Filter and display diagrams based on search and filter criteria"""
        # Clear existing diagram cards
        for widget in self.diagrams_scroll.winfo_children():
            widget.destroy()

        if self.role == ROLE_ADMIN:
            self.selected_diagrams.clear()
            self.diagram_checkboxes.clear()

        # Get search term and filter
        search_term = getattr(self, 'search_entry', None)
        search_term = search_term.get().lower() if search_term else ""

        pcb_filter = getattr(self, 'pcb_filter_combo', None)
        pcb_filter = pcb_filter.get() if pcb_filter else "All Types"

        # Filter diagrams
        filtered_diagrams = []
        for diag in self.diagrams_data:
            # Apply search filter
            name = diag.get('diagram_name', '').lower()
            description = diag.get('description', '').lower()
            if search_term and search_term not in name and search_term not in description:
                continue

            # Apply PCB type filter
            if pcb_filter != "All Types" and diag.get('description', 'N/A') != pcb_filter:
                continue

            filtered_diagrams.append(diag)

        # Update count
        self.count_label.configure(text=f"Showing {len(filtered_diagrams)} of {len(self.diagrams_data)} diagrams")

        # Display filtered diagrams
        if not filtered_diagrams:
            if not self.diagrams_data:
                no_data_label = ctk.CTkLabel(
                    self.diagrams_scroll,
                    text="📭 No diagrams uploaded yet",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                no_data_label.pack(pady=30)
            else:
                no_results_label = ctk.CTkLabel(
                    self.diagrams_scroll,
                    text="🔍 No diagrams match your search criteria",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                no_results_label.pack(pady=30)
            return

        # Create diagram cards
        for diag in filtered_diagrams:
            self.create_diagram_card(diag)

    def create_diagram_card(self, diagram: DBRecord) -> None:
        """Create a modern card for each diagram"""
        card_frame = ctk.CTkFrame(self.diagrams_scroll)
        card_frame.pack(fill="x", padx=5, pady=5)

        # Main content frame
        content_frame = ctk.CTkFrame(card_frame)
        content_frame.pack(fill="x", padx=10, pady=10)

        # Top row with checkbox (if admin) and diagram name
        top_row = ctk.CTkFrame(content_frame)
        top_row.pack(fill="x", pady=(0, 5))

        if self.role == ROLE_ADMIN:
            # Checkbox for bulk operations
            checkbox_var = ctk.BooleanVar()
            checkbox = ctk.CTkCheckBox(
                top_row,
                text="",
                variable=checkbox_var,
                width=20,
                command=lambda: self.on_diagram_checkbox_changed(diagram['id'], checkbox_var.get())
            )
            checkbox.pack(side="left", padx=(0, 10))
            self.diagram_checkboxes[diagram['id']] = checkbox_var

        # Diagram icon and name
        icon_frame = ctk.CTkFrame(top_row)
        icon_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            icon_frame,
            text="📋",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=(0, 5))

        name_label = ctk.CTkLabel(
            icon_frame,
            text=diagram.get('diagram_name', 'Untitled'),
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)

        # Upload date (right aligned)
        upload_date = diagram.get('uploaded_at', '')
        if upload_date:
            try:
                from datetime import datetime
                if isinstance(upload_date, str):
                    date_obj = datetime.strptime(upload_date[:19], '%Y-%m-%d %H:%M:%S')
                else:
                    date_obj = upload_date
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = str(upload_date)[:10]

            date_label = ctk.CTkLabel(
                top_row,
                text=date_str,
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            date_label.pack(side="right")

        # PCB Type
        pcb_type = diagram.get('description', 'N/A')
        type_label = ctk.CTkLabel(
            content_frame,
            text=f"📦 PCB Type: {pcb_type}",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        type_label.pack(fill="x", pady=(0, 5))

        # Action buttons
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(fill="x", pady=(5, 0))

        # View button
        view_btn = ctk.CTkButton(
            button_frame,
            text="👁️ View",
            width=80,
            height=30,
            fg_color="#007bff",
            hover_color="#0056b3",
            command=lambda d=diagram: self.select_and_display_diagram(d)
        )
        view_btn.pack(side="left", padx=(0, 5))

        # Edit button (Admin only)
        if self.role == ROLE_ADMIN:
            edit_btn = ctk.CTkButton(
                button_frame,
                text="✏️ Edit",
                width=80,
                height=30,
                fg_color="#28a745",
                hover_color="#218838",
                command=lambda d=diagram: self.edit_diagram(d)
            )
            edit_btn.pack(side="left", padx=5)

            delete_btn = ctk.CTkButton(
                button_frame,
                text="🗑️ Delete",
                width=80,
                height=30,
                fg_color="#dc3545",
                hover_color="#c82333",
                command=lambda d=diagram: self.delete_single_diagram(d)
            )
            delete_btn.pack(side="right")

    def select_and_display_diagram(self, diagram: DBRecord) -> None:
        """Select and display a diagram"""
        self.current_diagram = diagram
        self.display_diagram()
        self.update_diagram_actions()

    def update_diagram_actions(self) -> None:
        """Update the action buttons in the header when a diagram is selected"""
        # Clear existing action buttons
        for widget in self.actions_frame.winfo_children():
            widget.destroy()

        if not self.current_diagram:
            self.actions_frame.pack_forget()
            return

        self.actions_frame.pack(side="right", padx=10)

        if self.role == ROLE_ADMIN:
            # Edit metadata button
            edit_meta_btn = ctk.CTkButton(
                self.actions_frame,
                text="✏️ Edit Info",
                width=100,
                height=30,
                command=lambda: self.edit_diagram(self.current_diagram)
            )
            edit_meta_btn.pack(side="left", padx=2)

            # Delete button
            delete_btn = ctk.CTkButton(
                self.actions_frame,
                text="🗑️ Delete",
                width=80,
                height=30,
                fg_color="#dc3545",
                hover_color="#c82333",
                command=lambda: self.delete_single_diagram(self.current_diagram)
            )
            delete_btn.pack(side="left", padx=2)

        # Download original button
        download_btn = ctk.CTkButton(
            self.actions_frame,
            text="💾 Download",
            width=100,
            height=30,
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            command=self.download_diagram
        )
        download_btn.pack(side="left", padx=2)

    def display_diagram(self) -> None:
        """Display the selected diagram with zoom support"""
        if not self.current_diagram:
            logger.warning("No diagram selected")
            return

        # Update title
        diagram_name = self.current_diagram.get('diagram_name', 'Untitled')
        self.diagram_title.configure(text=f"📋 {diagram_name}")

        # Use correct key name from database: file_path
        diagram_path: str = self.current_diagram.get('file_path', '')

        if not os.path.exists(diagram_path):
            logger.error(f"Diagram file not found: {diagram_path}")
            self.image_label.configure(
                image=None,
                text=f"❌ File not found: {os.path.basename(diagram_path)}"
            )
            return

        try:
            # Load original image
            self.original_image = Image.open(diagram_path)
            logger.info(f"Loaded diagram: {diagram_path}, Size: {self.original_image.size}")

            # Apply current zoom level
            self.apply_zoom()

        except Exception as e:
            logger.error(f"Failed to load diagram: {str(e)}")
            self.image_label.configure(
                image=None,
                text=f"❌ Error loading image: {str(e)}"
            )

    def apply_zoom(self) -> None:
        """Apply current zoom level to the image"""
        if not self.original_image:
            return

        try:
            zoom_level = self.zoom_var.get()

            # Calculate new size
            original_width, original_height = self.original_image.size
            new_width = int(original_width * zoom_level)
            new_height = int(original_height * zoom_level)

            # Resize image
            if zoom_level == 1.0:
                # For 100% zoom, limit to reasonable display size
                max_width, max_height = 800, 600
                if new_width > max_width or new_height > max_height:
                    # Calculate ratio to fit within bounds
                    ratio = min(max_width/new_width, max_height/new_height)
                    new_width = int(new_width * ratio)
                    new_height = int(new_height * ratio)

            resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Create CTkImage
            photo = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(new_width, new_height))

            self.image_label.configure(image=photo, text="")
            self.current_image = photo  # Keep reference to prevent garbage collection

            # Update zoom label
            self.zoom_label.configure(text=f"{int(zoom_level*100)}%")

            logger.info(f"Applied zoom {zoom_level:.1f}x, Size: {new_width}x{new_height}")

        except Exception as e:
            logger.error(f"Failed to apply zoom: {str(e)}")

    # New methods for enhanced functionality
    def on_search_changed(self, event) -> None:
        """Handle search text changes"""
        self.filter_and_display_diagrams()

    def on_filter_changed(self, choice: str) -> None:
        """Handle PCB type filter changes"""
        self.filter_and_display_diagrams()

    def clear_search(self) -> None:
        """Clear search and filter"""
        self.search_entry.delete(0, 'end')
        self.pcb_filter_combo.set("All Types")
        self.filter_and_display_diagrams()

    def on_zoom_changed(self, value) -> None:
        """Handle zoom slider changes"""
        self.apply_zoom()

    def reset_zoom(self) -> None:
        """Reset zoom to 100%"""
        self.zoom_var.set(1.0)
        self.apply_zoom()

    def on_diagram_checkbox_changed(self, diagram_id: int, is_checked: bool) -> None:
        """Handle individual diagram checkbox changes"""
        if is_checked:
            self.selected_diagrams.add(diagram_id)
        else:
            self.selected_diagrams.discard(diagram_id)

        # Update select all checkbox
        total_diagrams = len(self.diagram_checkboxes)
        selected_count = len(self.selected_diagrams)

        if hasattr(self, 'select_all_var'):
            if selected_count == 0:
                self.select_all_var.set(False)
            elif selected_count == total_diagrams:
                self.select_all_var.set(True)

    def toggle_select_all(self) -> None:
        """Toggle select all diagrams"""
        select_all = self.select_all_var.get()

        for diagram_id, checkbox_var in self.diagram_checkboxes.items():
            checkbox_var.set(select_all)
            if select_all:
                self.selected_diagrams.add(diagram_id)
            else:
                self.selected_diagrams.discard(diagram_id)

    def bulk_delete_diagrams(self) -> None:
        """Delete selected diagrams"""
        if not self.selected_diagrams:
            messagebox.showwarning("Selection Required", "Please select diagrams to delete.")
            return

        count = len(self.selected_diagrams)
        if messagebox.askyesno("Confirm Bulk Delete", f"Delete {count} selected diagram(s)?\n\nThis action cannot be undone."):
            deleted_count = 0
            errors = []

            for diagram_id in list(self.selected_diagrams):
                try:
                    # Find diagram data
                    diagram = next((d for d in self.diagrams_data if d['id'] == diagram_id), None)
                    if diagram:
                        # Delete file
                        file_path = diagram.get('file_path', '')
                        if os.path.exists(file_path):
                            os.remove(file_path)

                        # Delete from database
                        if self.db.delete_jig_diagram(diagram_id):
                            deleted_count += 1
                        else:
                            errors.append(f"Failed to delete {diagram.get('diagram_name', 'Unknown')}")
                except Exception as e:
                    errors.append(f"Error deleting diagram ID {diagram_id}: {str(e)}")

            # Show results
            if deleted_count > 0:
                messagebox.showinfo("Success", f"Successfully deleted {deleted_count} diagram(s).")

            if errors:
                messagebox.showerror("Partial Success", f"Deleted {deleted_count} diagrams, but encountered errors:\n" + "\n".join(errors[:3]))

            # Refresh the list
            self.load_diagrams()

            # Clear current diagram if it was deleted
            if self.current_diagram and self.current_diagram['id'] in self.selected_diagrams:
                self.current_diagram = None
                self.original_image = None
                self.image_label.configure(image=None, text="📋 Select a diagram from the list to view it here")
                self.diagram_title.configure(text="Select a diagram to view")
                self.update_diagram_actions()

    def edit_diagram(self, diagram: DBRecord) -> None:
        """Edit diagram metadata"""
        edit_dialog = ctk.CTkToplevel(self)
        edit_dialog.title("Edit Diagram")
        edit_dialog.geometry("400x300")
        edit_dialog.attributes('-topmost', True)
        edit_dialog.grab_set()

        # Center dialog
        edit_dialog.update_idletasks()
        x = (edit_dialog.winfo_screenwidth() // 2) - 200
        y = (edit_dialog.winfo_screenheight() // 2) - 150
        edit_dialog.geometry(f'400x300+{x}+{y}')

        container = ctk.CTkFrame(edit_dialog)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            container,
            text="✏️ Edit Diagram Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        # Current values
        current_name = diagram.get('diagram_name', '')
        current_description = diagram.get('description', '')

        # Diagram name
        ctk.CTkLabel(container, text="Diagram Name:").pack(pady=5)
        name_entry = ctk.CTkEntry(container, width=300)
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)

        # PCB Type/Description
        ctk.CTkLabel(container, text="PCB Type:").pack(pady=5)
        desc_entry = ctk.CTkEntry(container, width=300)
        desc_entry.pack(pady=5)
        desc_entry.insert(0, current_description)

        def save_changes():
            new_name = name_entry.get().strip()
            new_description = desc_entry.get().strip()

            if not new_name:
                messagebox.showerror("Error", "Diagram name cannot be empty")
                return

            try:
                # Update database
                self.cursor = self.db.cursor
                self.cursor.execute(
                    "UPDATE jig_diagrams SET diagram_name=%s, description=%s WHERE id=%s",
                    (new_name, new_description, diagram['id'])
                )
                self.db.conn.commit()

                messagebox.showinfo("Success", "Diagram information updated successfully!")
                edit_dialog.destroy()
                self.load_diagrams()

                # Update current diagram if it's the one being edited
                if self.current_diagram and self.current_diagram['id'] == diagram['id']:
                    self.current_diagram['diagram_name'] = new_name
                    self.current_diagram['description'] = new_description
                    self.diagram_title.configure(text=f"📋 {new_name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update diagram: {str(e)}")

        # Buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=20)

        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            width=120,
            command=save_changes
        )
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            fg_color="gray",
            command=edit_dialog.destroy
        )
        cancel_btn.pack(side="left", padx=5)

    def delete_single_diagram(self, diagram: DBRecord) -> None:
        """Delete a single diagram"""
        diagram_name = diagram.get('diagram_name', 'Unknown')
        if messagebox.askyesno("Confirm Delete", f"Delete diagram '{diagram_name}'?\n\nThis action cannot be undone."):
            try:
                # Delete file
                file_path = diagram.get('file_path', '')
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted diagram file: {file_path}")

                # Delete from database
                if self.db.delete_jig_diagram(diagram['id']):
                    messagebox.showinfo("Success", "Diagram deleted successfully!")
                    logger.info(f"Deleted diagram from database: {diagram_name}")

                    # Clear current diagram if it was deleted
                    if self.current_diagram and self.current_diagram['id'] == diagram['id']:
                        self.current_diagram = None
                        self.original_image = None
                        self.image_label.configure(image=None, text="📋 Select a diagram from the list to view it here")
                        self.diagram_title.configure(text="Select a diagram to view")
                        self.update_diagram_actions()

                    self.load_diagrams()
                else:
                    messagebox.showerror("Error", "Failed to delete diagram from database")

            except Exception as e:
                logger.error(f"Error deleting diagram: {e}")
                messagebox.showerror("Error", f"Error deleting diagram: {str(e)}")

    def download_diagram(self) -> None:
        """Download the current diagram"""
        if not self.current_diagram:
            return

        file_path = self.current_diagram.get('file_path', '')
        if not os.path.exists(file_path):
            messagebox.showerror("Error", "Diagram file not found")
            return

        # Ask for save location
        original_filename = os.path.basename(file_path)
        save_path = filedialog.asksaveasfilename(
            title="Save Diagram As",
            defaultextension=os.path.splitext(original_filename)[1],
            initialfilename=original_filename,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )

        if save_path:
            try:
                import shutil
                shutil.copy2(file_path, save_path)
                messagebox.showinfo("Success", f"Diagram saved to {save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save diagram: {str(e)}")
    
    def upload_diagram(self) -> None:
        """Upload a new diagram with enhanced preview (Admin only)"""
        # Ask for image file
        file_path: str = filedialog.askopenfilename(
            title="Select Jig Diagram Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        # Create enhanced upload dialog with preview
        upload_dialog: ctk.CTkToplevel = ctk.CTkToplevel(self)
        upload_dialog.title("📁 Upload New Diagram")
        upload_dialog.geometry("700x600")

        # Make window appear on top
        upload_dialog.attributes('-topmost', True)
        upload_dialog.lift()
        upload_dialog.focus_force()
        upload_dialog.grab_set()

        # Center dialog
        upload_dialog.update_idletasks()
        x: int = (upload_dialog.winfo_screenwidth() // 2) - 350
        y: int = (upload_dialog.winfo_screenheight() // 2) - 300
        upload_dialog.geometry(f'700x600+{x}+{y}')

        # Main container
        main_container = ctk.CTkFrame(upload_dialog)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title with file info
        title_frame = ctk.CTkFrame(main_container)
        title_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(
            title_frame,
            text="📁 Upload New Diagram",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=10)

        # Selected file info
        filename = os.path.basename(file_path)
        try:
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            file_info = f"📄 File: {filename} ({file_size:.1f} MB)"
        except:
            file_info = f"📄 File: {filename}"

        ctk.CTkLabel(
            title_frame,
            text=file_info,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack()

        # Two-column layout
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Left side - Form fields
        form_frame = ctk.CTkFrame(content_frame)
        form_frame.pack(side="left", fill="y", padx=(0, 10))
        form_frame.configure(width=300)

        ctk.CTkLabel(
            form_frame,
            text="📝 Diagram Information",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 20))

        # Form fields
        fields_frame = ctk.CTkFrame(form_frame)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Diagram name
        ctk.CTkLabel(fields_frame, text="Diagram Name:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 5))
        name_entry = ctk.CTkEntry(
            fields_frame,
            width=260,
            height=35,
            placeholder_text="e.g., Main Test Jig V2.0"
        )
        name_entry.pack(pady=(0, 15))

        # PCB Type
        ctk.CTkLabel(fields_frame, text="PCB Type:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))

        # Get existing PCB types for dropdown
        existing_types = set()
        for diag in self.diagrams_data:
            pcb_type = diag.get('description', '')
            if pcb_type and pcb_type != 'N/A':
                existing_types.add(pcb_type)

        pcb_types = [""] + sorted(list(existing_types)) + ["Other (type below)"]

        pcb_combo = ctk.CTkComboBox(
            fields_frame,
            width=260,
            height=35,
            values=pcb_types,
            command=lambda choice: self.on_pcb_type_selected(choice, pcb_entry)
        )
        pcb_combo.pack(pady=(0, 5))

        pcb_entry = ctk.CTkEntry(
            fields_frame,
            width=260,
            height=35,
            placeholder_text="e.g., Power Board, Control Unit"
        )
        pcb_entry.pack(pady=(0, 15))

        # Description
        ctk.CTkLabel(fields_frame, text="Description (Optional):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(0, 5))
        desc_text = ctk.CTkTextbox(
            fields_frame,
            width=260,
            height=80
        )
        desc_text.pack(pady=(0, 10))

        # Associate with test case (optional)
        ctk.CTkLabel(fields_frame, text="Link to Test Case (Optional):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10, 5))

        # Get available test cases
        test_cases = self.db.get_test_cases()
        test_case_options = ["None"] + [f"{tc['name']} (ID: {tc['id']})" for tc in test_cases]

        testcase_combo = ctk.CTkComboBox(
            fields_frame,
            width=260,
            height=35,
            values=test_case_options
        )
        testcase_combo.pack()

        # Right side - Image preview
        preview_frame = ctk.CTkFrame(content_frame)
        preview_frame.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            preview_frame,
            text="🖼️ Preview",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 15))

        # Image preview area
        preview_scroll = ctk.CTkScrollableFrame(preview_frame, height=400)
        preview_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Load and display preview
        try:
            preview_image = Image.open(file_path)
            # Resize for preview (max 350x250)
            preview_image.thumbnail((350, 250), Image.Resampling.LANCZOS)

            preview_photo = ctk.CTkImage(
                light_image=preview_image,
                dark_image=preview_image,
                size=preview_image.size
            )

            preview_label = ctk.CTkLabel(preview_scroll, image=preview_photo, text="")
            preview_label.pack(pady=20)

            # Image info
            original_size = Image.open(file_path).size
            info_text = f"Original Size: {original_size[0]} × {original_size[1]} pixels"
            size_label = ctk.CTkLabel(
                preview_frame,
                text=info_text,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            size_label.pack()

        except Exception as e:
            error_label = ctk.CTkLabel(
                preview_scroll,
                text=f"❌ Could not preview image\n{str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=50)

        # Auto-fill name from filename
        base_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        name_entry.insert(0, base_name)

        def save_diagram() -> None:
            name: str = name_entry.get().strip()
            pcb_from_combo = pcb_combo.get().strip()
            pcb_from_entry = pcb_entry.get().strip()

            # Determine PCB type
            if pcb_from_combo and pcb_from_combo not in ["", "Other (type below)"]:
                pcb_type = pcb_from_combo
            else:
                pcb_type = pcb_from_entry

            description = desc_text.get("1.0", "end-1c").strip()

            # Get test case ID if selected
            test_case_id = None
            testcase_selection = testcase_combo.get()
            if testcase_selection != "None":
                try:
                    test_case_id = int(testcase_selection.split("ID: ")[1].split(")")[0])
                except:
                    pass

            # Validation
            if not name:
                messagebox.showerror("Validation Error", "Please enter a diagram name")
                name_entry.focus()
                return

            if not pcb_type:
                messagebox.showerror("Validation Error", "Please specify a PCB type")
                if pcb_from_combo == "Other (type below)":
                    pcb_entry.focus()
                else:
                    pcb_combo.focus()
                return

            # Create diagrams directory if it doesn't exist
            diagrams_dir: str = "assets/diagrams"
            os.makedirs(diagrams_dir, exist_ok=True)

            # Generate unique filename to avoid conflicts
            original_ext = os.path.splitext(filename)[1]
            safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{safe_name}_{timestamp}{original_ext}"
            dest_path: str = os.path.join(diagrams_dir, new_filename)

            try:
                # Show progress
                progress_label = ctk.CTkLabel(
                    main_container,
                    text="💾 Saving diagram...",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#007bff"
                )
                progress_label.pack(pady=10)
                upload_dialog.update()

                # Copy file to diagrams directory
                import shutil
                shutil.copy2(file_path, dest_path)
                logger.info(f"Copied diagram file to: {dest_path}")

                # Get user_id for uploaded_by parameter
                user_id: Optional[int] = self.db.get_user_id(self.username)

                # Save to database
                diagram_id: Optional[int] = self.db.save_jig_diagram(
                    test_case_id=test_case_id,
                    diagram_name=name,
                    file_path=dest_path,
                    description=pcb_type,
                    uploaded_by=user_id
                )

                if diagram_id:
                    logger.info(f"Diagram saved with ID: {diagram_id}, Name: {name}")

                    success_msg = f"✅ Diagram uploaded successfully!\n\nName: {name}\nPCB Type: {pcb_type}\nFile: {new_filename}"
                    if test_case_id:
                        success_msg += f"\nLinked to Test Case ID: {test_case_id}"

                    messagebox.showinfo("Success", success_msg)
                    upload_dialog.destroy()
                    self.load_diagrams()
                else:
                    logger.error("Failed to save diagram to database")
                    messagebox.showerror("Error", "Failed to save diagram to database")

            except Exception as e:
                logger.error(f"Failed to upload diagram: {str(e)}")
                messagebox.showerror("Error", f"Failed to upload diagram:\n{str(e)}")
            finally:
                # Remove progress label if it exists
                try:
                    progress_label.destroy()
                except:
                    pass

        # Bottom buttons
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(fill="x", pady=(10, 0))

        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Upload Diagram",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            command=save_diagram
        )
        save_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=120,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=upload_dialog.destroy
        )
        cancel_btn.pack(side="right", padx=(10, 5))

        # Focus on name entry
        name_entry.focus()

    def on_pcb_type_selected(self, choice: str, pcb_entry: ctk.CTkEntry) -> None:
        """Handle PCB type selection"""
        if choice == "Other (type below)":
            pcb_entry.focus()
        elif choice:
            pcb_entry.delete(0, 'end')
            pcb_entry.insert(0, choice)
    

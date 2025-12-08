"""
Communication Configuration Window - COM Port Settings
"""
import customtkinter as ctk
from tkinter import messagebox
import serial.tools.list_ports
from data.database import Database

class CommunicationConfigWindow(ctk.CTkToplevel):
    def __init__(self, parent, username, role):
        super().__init__(parent)
        
        self.username = username
        self.role = role
        self.db = Database()
        
        self.title("Communication Configuration")
        self.geometry("700x600")
        
        self.center_window()
        self.create_widgets()
        self.load_config()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 700
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create communication config UI"""
        # Main container
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Communication Configuration",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Warning
        warning_label = ctk.CTkLabel(
            container,
            text="⚠️ Admin Only - Changes affect all test stations",
            font=ctk.CTkFont(size=12),
            text_color="orange"
        )
        warning_label.pack(pady=5)
        
        # Configuration frame
        config_frame = ctk.CTkFrame(container)
        config_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # COM Port
        port_frame = ctk.CTkFrame(config_frame)
        port_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(port_frame, text="COM Port:", width=150).pack(side="left", padx=10)
        self.port_combo = ctk.CTkComboBox(
            port_frame,
            values=self.get_available_ports(),
            width=200
        )
        self.port_combo.pack(side="left", padx=10)
        
        refresh_btn = ctk.CTkButton(
            port_frame,
            text="Refresh",
            width=80,
            command=self.refresh_ports
        )
        refresh_btn.pack(side="left", padx=5)
        
        # Baud Rate
        baud_frame = ctk.CTkFrame(config_frame)
        baud_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(baud_frame, text="Baud Rate:", width=150).pack(side="left", padx=10)
        self.baud_combo = ctk.CTkComboBox(
            baud_frame,
            values=["9600", "19200", "38400", "57600", "115200"],
            width=200
        )
        self.baud_combo.set("9600")
        self.baud_combo.pack(side="left", padx=10)
        
        # Data Bits
        data_frame = ctk.CTkFrame(config_frame)
        data_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(data_frame, text="Data Bits:", width=150).pack(side="left", padx=10)
        self.data_combo = ctk.CTkComboBox(
            data_frame,
            values=["5", "6", "7", "8"],
            width=200
        )
        self.data_combo.set("8")
        self.data_combo.pack(side="left", padx=10)
        
        # Parity
        parity_frame = ctk.CTkFrame(config_frame)
        parity_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(parity_frame, text="Parity:", width=150).pack(side="left", padx=10)
        self.parity_combo = ctk.CTkComboBox(
            parity_frame,
            values=["None", "Even", "Odd", "Mark", "Space"],
            width=200
        )
        self.parity_combo.set("None")
        self.parity_combo.pack(side="left", padx=10)
        
        # Stop Bits
        stop_frame = ctk.CTkFrame(config_frame)
        stop_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(stop_frame, text="Stop Bits:", width=150).pack(side="left", padx=10)
        self.stop_combo = ctk.CTkComboBox(
            stop_frame,
            values=["1", "1.5", "2"],
            width=200
        )
        self.stop_combo.set("1")
        self.stop_combo.pack(side="left", padx=10)
        
        # Timeout
        timeout_frame = ctk.CTkFrame(config_frame)
        timeout_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(timeout_frame, text="Timeout (seconds):", width=150).pack(side="left", padx=10)
        self.timeout_entry = ctk.CTkEntry(timeout_frame, width=200, placeholder_text="e.g., 5")
        self.timeout_entry.insert(0, "5")
        self.timeout_entry.pack(side="left", padx=10)
        
        # Connection status
        self.status_label = ctk.CTkLabel(
            config_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=20)
        
        test_btn = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            width=150,
            height=40,
            command=self.test_connection
        )
        test_btn.pack(side="left", padx=10)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save Configuration",
            width=150,
            height=40,
            command=self.save_config
        )
        save_btn.pack(side="left", padx=10)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            width=150,
            height=40,
            fg_color="red",
            hover_color="darkred",
            command=self.destroy
        )
        close_btn.pack(side="left", padx=10)
    
    def get_available_ports(self):
        """Get list of available COM ports"""
        ports = serial.tools.list_ports.comports()
        if ports:
            return [port.device for port in ports]
        return ["No ports available"]
    
    def refresh_ports(self):
        """Refresh the list of available COM ports"""
        ports = self.get_available_ports()
        self.port_combo.configure(values=ports)
        if ports and ports[0] != "No ports available":
            self.port_combo.set(ports[0])
        messagebox.showinfo("Refreshed", f"Found {len(ports)} port(s)")
    
    def test_connection(self):
        """Test the serial connection"""
        port = self.port_combo.get()
        
        if port == "No ports available":
            messagebox.showerror("Error", "No COM port selected")
            return
        
        try:
            baud_rate = int(self.baud_combo.get())
            timeout = float(self.timeout_entry.get())
            
            # Try to open connection
            ser = serial.Serial(
                port=port,
                baudrate=baud_rate,
                timeout=timeout
            )
            
            if ser.is_open:
                self.status_label.configure(
                    text=f"✓ Connection successful on {port}",
                    text_color="green"
                )
                ser.close()
                messagebox.showinfo("Success", f"Successfully connected to {port}")
            else:
                self.status_label.configure(
                    text="✗ Failed to open connection",
                    text_color="red"
                )
                messagebox.showerror("Error", "Failed to open connection")
                
        except serial.SerialException as e:
            self.status_label.configure(
                text=f"✗ Connection failed: {str(e)}",
                text_color="red"
            )
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid configuration: {str(e)}")
    
    def save_config(self):
        """Save communication configuration"""
        port = self.port_combo.get()
        
        if port == "No ports available":
            messagebox.showerror("Error", "No COM port selected")
            return
        
        try:
            baud_rate = int(self.baud_combo.get())
            data_bits = int(self.data_combo.get())
            timeout = float(self.timeout_entry.get())
            
            config = {
                'port': port,
                'baud_rate': baud_rate,
                'data_bits': data_bits,
                'parity': self.parity_combo.get(),
                'stop_bits': self.stop_combo.get(),
                'timeout': timeout
            }
            
            success = self.db.save_comm_config(config, self.username)
            
            if success:
                messagebox.showinfo("Success", "Configuration saved successfully!")
            else:
                messagebox.showerror("Error", "Failed to save configuration")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid configuration: {str(e)}")
    
    def load_config(self):
        """Load saved configuration"""
        config = self.db.get_comm_config()
        
        if config:
            self.port_combo.set(config.get('port', ''))
            self.baud_combo.set(str(config.get('baud_rate', '9600')))
            self.data_combo.set(str(config.get('data_bits', '8')))
            self.parity_combo.set(config.get('parity', 'None'))
            self.stop_combo.set(str(config.get('stop_bits', '1')))
            self.timeout_entry.delete(0, 'end')
            self.timeout_entry.insert(0, str(config.get('timeout', '5')))

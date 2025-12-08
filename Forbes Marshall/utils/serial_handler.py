"""
Serial Communication Handler
"""
import serial
import threading
import queue
import time
from data.database import Database

class SerialHandler:
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.data_queue = queue.Queue()
        self.stop_reading = False
        self.db = Database()
    
    def connect(self):
        """Connect to serial port using saved configuration"""
        config = self.db.get_comm_config()
        
        if not config:
            raise Exception("No communication configuration found. Please configure in settings.")
        
        try:
            # Map parity string to serial constant
            parity_map = {
                'None': serial.PARITY_NONE,
                'Even': serial.PARITY_EVEN,
                'Odd': serial.PARITY_ODD,
                'Mark': serial.PARITY_MARK,
                'Space': serial.PARITY_SPACE
            }
            
            # Map stop bits string to serial constant
            stopbits_map = {
                '1': serial.STOPBITS_ONE,
                '1.5': serial.STOPBITS_ONE_POINT_FIVE,
                '2': serial.STOPBITS_TWO
            }
            
            self.serial_port = serial.Serial(
                port=config['port'],
                baudrate=config['baud_rate'],
                bytesize=config['data_bits'],
                parity=parity_map.get(config['parity'], serial.PARITY_NONE),
                stopbits=stopbits_map.get(config['stop_bits'], serial.STOPBITS_ONE),
                timeout=config['timeout']
            )
            
            self.is_connected = True
            self.start_reading()
            return True
            
        except serial.SerialException as e:
            raise Exception(f"Failed to connect: {str(e)}")
    
    def disconnect(self):
        """Disconnect from serial port"""
        self.stop_reading = True
        
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.is_connected = False
    
    def start_reading(self):
        """Start reading data in background thread"""
        self.stop_reading = False
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()
    
    def _read_loop(self):
        """Background thread for reading serial data"""
        while not self.stop_reading and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        self.data_queue.put(data)
                time.sleep(0.01)  # Small delay to prevent CPU spinning
            except Exception as e:
                print(f"Error reading serial data: {e}")
                break
    
    def write(self, data):
        """Write data to serial port"""
        if not self.is_connected or not self.serial_port:
            raise Exception("Not connected to serial port")
        
        try:
            self.serial_port.write(data.encode('utf-8'))
            return True
        except Exception as e:
            raise Exception(f"Failed to write data: {str(e)}")
    
    def read(self, timeout=1.0):
        """Read data from queue with timeout"""
        try:
            return self.data_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def read_test_data(self):
        """
        Read test data from PCB
        Expected format: "V:5.0,C:0.5,R:100.0"
        Returns dict with voltage, current, resistance
        """
        data = self.read(timeout=5.0)
        
        if not data:
            raise Exception("No data received from PCB")
        
        try:
            # Parse data
            parts = data.split(',')
            result = {}
            
            for part in parts:
                key, value = part.split(':')
                key = key.strip().upper()
                value = float(value.strip())
                
                if key == 'V':
                    result['voltage'] = value
                elif key == 'C':
                    result['current'] = value
                elif key == 'R':
                    result['resistance'] = value
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to parse test data: {str(e)}")
    
    def send_command(self, command):
        """Send command to PCB and wait for acknowledgment"""
        self.write(command + '\n')
        
        # Wait for ACK
        response = self.read(timeout=2.0)
        
        if response and 'ACK' in response:
            return True
        
        return False

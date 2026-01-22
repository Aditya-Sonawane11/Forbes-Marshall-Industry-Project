"""
Serial Communication Handler
"""
import serial
import serial.tools.list_ports
import threading
import queue
import time
import logging
from data.database import Database

# Set up logger for this module
logger = logging.getLogger(__name__)

class SerialHandler:
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.read_thread = None
        self.data_queue = queue.Queue()
        self.stop_reading = False
        self.db = Database()
    
    @staticmethod
    def get_available_ports():
        """Get list of available COM ports"""
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(f"{port.device} ({port.description})")
        return ports
    
    def connect(self):
        """Connect to serial port using saved configuration"""
        logger.info("=" * 60)
        logger.info("Attempting serial connection...")
        logger.info("=" * 60)
        
        config = self.db.get_comm_config()
        
        if not config:
            logger.error("No communication configuration found in database")
            available_ports = self.get_available_ports()
            logger.info(f"Available ports detected: {available_ports}")
            ports_info = "\n".join(available_ports) if available_ports else "No ports found"
            error_msg = f"No communication configuration found. Please configure in settings.\n\nAvailable ports:\n{ports_info}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        try:
            # Get port from config - handle both 'port' and 'com_port' key names
            port = config.get('com_port') or config.get('port')
            baud_rate = config.get('baud_rate')
            data_bits = config.get('data_bits')
            timeout = config.get('timeout_seconds') or config.get('timeout')
            
            logger.info(f"Configuration loaded: Port={port}, BaudRate={baud_rate}, DataBits={data_bits}, Timeout={timeout}")
            
            # Check if configured port exists
            available_ports_list = [p.split()[0] for p in self.get_available_ports()]  # Extract just the port name
            
            if port not in available_ports_list:
                logger.warning(f"Configured port {port} not available on system")
                available_ports = self.get_available_ports()
                ports_info = "\n".join(available_ports) if available_ports else "No ports found"
                
                # Suggest the first available port
                suggestion = ""
                if available_ports_list:
                    suggestion = f"\n\n[SUGGESTION] Use {available_ports_list[0]} instead and save in Communication Settings."
                
                error_msg = f"Configured port '{port}' is not available on this system.{suggestion}\n\nAvailable ports:\n{ports_info}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
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
            
            logger.info(f"Opening serial port: {port}")
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baud_rate,
                bytesize=data_bits,
                parity=parity_map.get(config.get('parity', 'None'), serial.PARITY_NONE),
                stopbits=stopbits_map.get(str(config.get('stop_bits', '1')), serial.STOPBITS_ONE),
                timeout=float(timeout) if timeout else 5.0
            )
            
            self.is_connected = True
            logger.info(f"✓ Serial port opened successfully on {port}")
            self.start_reading()
            logger.info("Background read thread started")
            return True
            
        except serial.SerialException as e:
            logger.error(f"Serial connection failed: {str(e)}")
            available_ports = self.get_available_ports()
            ports_info = "\n".join(available_ports) if available_ports else "No ports found"
            logger.error(f"Available ports: {ports_info}")
            error_msg = f"Failed to connect to {config.get('com_port') or config.get('port')}: {str(e)}\n\nAvailable ports:\n{ports_info}"
            raise Exception(error_msg)
    
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
        Expected format: 
        235,Voltage,4.4
        235,resistance,1
        235,current,0
        
        Returns dict with voltage, current, resistance
        """
        result = {}
        timeout_counter = 0
        max_attempts = 10  # Try reading up to 10 lines
        
        logger.info("Reading test data from PCB...")
        
        while timeout_counter < max_attempts:
            data = self.read(timeout=2.0)
            
            if not data:
                timeout_counter += 1
                continue
            
            try:
                # Parse CSV format: PCB_ID,Parameter,Value
                parts = data.strip().split(',')
                
                if len(parts) < 3:
                    logger.warning(f"Invalid data format: {data}")
                    continue
                
                pcb_id = parts[0].strip()
                parameter = parts[1].strip().lower()
                value = float(parts[2].strip())
                
                logger.info(f"Parsed - PCB ID: {pcb_id}, Parameter: {parameter}, Value: {value}")
                
                # Map parameter names to result keys
                if parameter == 'voltage':
                    result['voltage'] = value
                elif parameter == 'current':
                    result['current'] = value
                elif parameter == 'resistance':
                    result['resistance'] = value
                
                # Check if we have all required values
                if len(result) == 3:
                    logger.info(f"All test data received: {result}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Failed to parse data line: {data} - {str(e)}")
                continue
        
        # Check if we got partial data
        if result:
            logger.warning(f"Incomplete data received, using what we have: {result}")
            # Fill in missing values with 0
            if 'voltage' not in result:
                result['voltage'] = 0
            if 'current' not in result:
                result['current'] = 0
            if 'resistance' not in result:
                result['resistance'] = 0
            return result
        
        raise Exception("No test data received from PCB after multiple attempts")
    
    def send_command(self, command):
        """Send command to PCB and wait for acknowledgment"""
        self.write(command + '\n')
        
        # Wait for ACK
        response = self.read(timeout=2.0)
        
        if response and 'ACK' in response:
            return True
        
        return False

"""
Hardware Interface Converters - USB, HDMI, Serial

text2usb, text3usb, text4usb - USB device communication
text2hdmi, text4hdmi - HDMI info and capture
text2serial, text3serial, text4serial - Serial port communication
"""

from typing import Dict, Any, Optional, List, Union
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.stream_base import BaseStreamConverter, StreamEvent, StreamConfig, StreamState
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# USB Data Types
# ============================================================================

@dataclass
class USBDevice:
    """Reprezentacja urządzenia USB"""
    vendor_id: str
    product_id: str
    manufacturer: str = ""
    product: str = ""
    serial: str = ""
    bus: int = 0
    device: int = 0
    speed: str = ""  # low, full, high, super
    
    @property
    def id(self) -> str:
        return f"{self.vendor_id}:{self.product_id}"
    
    def to_dict(self) -> Dict:
        return {
            "vendor_id": self.vendor_id,
            "product_id": self.product_id,
            "manufacturer": self.manufacturer,
            "product": self.product,
            "serial": self.serial,
            "bus": self.bus,
            "device": self.device,
            "speed": self.speed
        }


@dataclass
class USBTransfer:
    """Transfer USB"""
    endpoint: int
    data: bytes
    direction: str  # in, out
    transfer_type: str  # control, bulk, interrupt, isochronous
    status: str = "pending"


# ============================================================================
# text2usb - Read USB Devices (READ)
# ============================================================================

class Text2USB(BaseConverter):
    """
    Czytnik USB.
    
    Funkcje:
    - Listowanie urządzeń
    - Informacje o urządzeniu
    - Odczyt danych
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę USB"""
        return f"usb_{intent.get('action', 'list')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję USB"""
        text = text.lower()
        
        action = "list"
        if "info" in text or "szczegóły" in text:
            action = "info"
        elif "read" in text or "odczytaj" in text:
            action = "read"
        elif "find" in text or "znajdź" in text:
            action = "find"
        
        # Extract device ID
        device_match = re.search(r'(\w{4}):(\w{4})', text)
        device_id = f"{device_match.group(1)}:{device_match.group(2)}" if device_match else None
        
        # Extract bus/device
        bus_match = re.search(r'bus\s*(\d+)', text)
        dev_match = re.search(r'device\s*(\d+)', text)
        bus = int(bus_match.group(1)) if bus_match else None
        device = int(dev_match.group(1)) if dev_match else None
        
        return {
            "action": action,
            "device_id": device_id,
            "bus": bus,
            "device": device,
            "description": text
        }
    
    def list_devices(self) -> List[USBDevice]:
        """Listuje urządzenia USB (symulacja)"""
        
        # Symulacja urządzeń
        return [
            USBDevice("046d", "c077", "Logitech", "USB Mouse", "", 1, 2, "full"),
            USBDevice("8087", "0024", "Intel Corp.", "USB Hub", "", 1, 1, "high"),
            USBDevice("0781", "5567", "SanDisk", "USB Flash Drive", "ABC123", 2, 3, "high"),
            USBDevice("1d6b", "0002", "Linux Foundation", "USB 2.0 Hub", "", 1, 1, "high"),
            USBDevice("04f2", "b604", "Chicony", "USB Camera", "", 1, 4, "high"),
        ]
    
    def get_device_info(self, device_id: str) -> Optional[USBDevice]:
        """Pobiera informacje o urządzeniu"""
        
        devices = self.list_devices()
        for dev in devices:
            if dev.id == device_id:
                return dev
        return None
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje operację USB"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["action"] == "list":
                devices = self.list_devices()
                output = "\n".join([f"{d.id} - {d.manufacturer} {d.product}" for d in devices])
                
                return ConversionResult(
                    success=True,
                    command="lsusb",
                    output=output,
                    metadata={
                        "action": "list",
                        "count": len(devices),
                        "devices": [d.to_dict() for d in devices]
                    }
                )
                
            elif intent["action"] == "info" and intent["device_id"]:
                device = self.get_device_info(intent["device_id"])
                
                if device:
                    output = f"""USB Device: {device.id}
Manufacturer: {device.manufacturer}
Product: {device.product}
Serial: {device.serial or 'N/A'}
Bus: {device.bus}, Device: {device.device}
Speed: {device.speed}"""
                    
                    return ConversionResult(
                        success=True,
                        command=f"lsusb -d {device.id} -v",
                        output=output,
                        metadata={
                            "action": "info",
                            "device": device.to_dict()
                        }
                    )
                else:
                    return ConversionResult(
                        success=False,
                        error=f"Device not found: {intent['device_id']}"
                    )
            
            elif intent["action"] == "find":
                devices = self.list_devices()
                # Filter by description
                search = intent["description"]
                found = [d for d in devices if search in d.product.lower() or search in d.manufacturer.lower()]
                
                output = "\n".join([f"{d.id} - {d.manufacturer} {d.product}" for d in found])
                
                return ConversionResult(
                    success=True,
                    command=f"lsusb | grep -i '{search}'",
                    output=output or "No devices found",
                    metadata={
                        "action": "find",
                        "count": len(found)
                    }
                )
            
            else:
                return ConversionResult(
                    success=False,
                    error="Unknown action or missing parameters"
                )
                
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3usb - Write USB (WRITE)
# ============================================================================

class Text3USB(BaseConverter):
    """
    Zapisywacz USB.
    
    Funkcje:
    - Wysyłanie danych do urządzenia
    - Konfiguracja urządzenia
    - Reset urządzenia
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę USB"""
        return f"usb_{intent.get('action', 'write')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję zapisu USB"""
        text = text.lower()
        
        action = "write"
        if "reset" in text:
            action = "reset"
        elif "config" in text or "konfigur" in text:
            action = "configure"
        
        # Device ID
        device_match = re.search(r'(\w{4}):(\w{4})', text)
        device_id = f"{device_match.group(1)}:{device_match.group(2)}" if device_match else None
        
        # Data
        data_match = re.search(r'data[:\s]+["\']?([^"\']+)["\']?', text)
        data = data_match.group(1) if data_match else None
        
        return {
            "action": action,
            "device_id": device_id,
            "data": data,
            "description": text
        }
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje zapis USB"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["action"] == "reset" and intent["device_id"]:
                return ConversionResult(
                    success=True,
                    command=f"usbreset {intent['device_id']}",
                    output=f"Device {intent['device_id']} reset successfully",
                    metadata={"action": "reset", "device_id": intent["device_id"]}
                )
                
            elif intent["action"] == "write":
                return ConversionResult(
                    success=True,
                    command=f"usb_write {intent['device_id']}",
                    output=f"Data written to {intent['device_id']}",
                    metadata={"action": "write", "device_id": intent["device_id"]}
                )
            
            else:
                return ConversionResult(
                    success=False,
                    error="Unknown action"
                )
                
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4usb - USB Streaming (STREAM)
# ============================================================================

class Text4USB(BaseStreamConverter):
    """
    USB data streaming.
    
    Funkcje:
    - Continuous data read
    - Device monitoring
    - Hot-plug events
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._device_id: str = None
        self._reader = Text2USB()
    
    async def connect(self, target: str) -> bool:
        """Połącz z urządzeniem USB"""
        try:
            self._device_id = target
            self.state = StreamState.CONNECTED
            logger.info(f"Connected to USB device: {target}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self._device_id = None
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Wyślij dane do urządzenia"""
        logger.info(f"Sending data to USB device: {self._device_id}")
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Odbiera dane z urządzenia USB"""
        
        import random
        
        # Symulacja danych (np. z sensora USB)
        data = {
            "timestamp": datetime.now().isoformat(),
            "value": random.uniform(0, 100),
            "status": "ok"
        }
        
        await asyncio.sleep(0.1)  # 10 Hz
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="usb_data",
            data=data,
            source=f"usb://{self._device_id}",
            metadata={"device_id": self._device_id}
        )


# ============================================================================
# HDMI Converters
# ============================================================================

@dataclass
class HDMIInfo:
    """Informacje HDMI"""
    port: int
    connected: bool
    resolution: str = ""
    refresh_rate: int = 0
    color_depth: int = 8
    audio: bool = True
    hdcp: bool = True
    manufacturer: str = ""
    model: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "port": self.port,
            "connected": self.connected,
            "resolution": self.resolution,
            "refresh_rate": self.refresh_rate,
            "color_depth": self.color_depth,
            "audio": self.audio,
            "hdcp": self.hdcp,
            "manufacturer": self.manufacturer,
            "model": self.model
        }


# ============================================================================
# text2hdmi - Read HDMI Info (READ)
# ============================================================================

class Text2HDMI(BaseConverter):
    """
    Czytnik informacji HDMI.
    
    Funkcje:
    - EDID parsing
    - Display info
    - Audio capabilities
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę HDMI"""
        return f"hdmi_{intent.get('action', 'info')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję HDMI"""
        text = text.lower()
        
        action = "info"
        if "edid" in text:
            action = "edid"
        elif "resolution" in text or "rozdzielczość" in text:
            action = "resolution"
        elif "audio" in text:
            action = "audio"
        
        # Port
        port_match = re.search(r'(?:port|hdmi)\s*(\d+)', text)
        port = int(port_match.group(1)) if port_match else 0
        
        return {
            "action": action,
            "port": port,
            "description": text
        }
    
    def get_hdmi_info(self, port: int = 0) -> HDMIInfo:
        """Pobiera informacje HDMI (symulacja)"""
        
        # Symulacja
        return HDMIInfo(
            port=port,
            connected=True,
            resolution="1920x1080",
            refresh_rate=60,
            color_depth=8,
            audio=True,
            hdcp=True,
            manufacturer="Samsung",
            model="U28E590"
        )
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje odczyt HDMI"""
        
        try:
            intent = self.parse_intent(text)
            info = self.get_hdmi_info(intent["port"])
            
            if intent["action"] == "info":
                output = f"""HDMI Port {info.port}
Connected: {info.connected}
Display: {info.manufacturer} {info.model}
Resolution: {info.resolution} @ {info.refresh_rate}Hz
Color Depth: {info.color_depth}-bit
Audio: {'Enabled' if info.audio else 'Disabled'}
HDCP: {'Enabled' if info.hdcp else 'Disabled'}"""
                
            elif intent["action"] == "resolution":
                output = f"{info.resolution} @ {info.refresh_rate}Hz"
                
            elif intent["action"] == "audio":
                output = f"Audio: {'Supported' if info.audio else 'Not supported'}"
                
            elif intent["action"] == "edid":
                output = "EDID: Raw EDID data (128 bytes)"
            
            else:
                output = str(info.to_dict())
            
            return ConversionResult(
                success=True,
                command=f"xrandr --verbose | grep HDMI-{intent['port']}",
                output=output,
                metadata={
                    "action": intent["action"],
                    "hdmi_info": info.to_dict()
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4hdmi - HDMI Capture Streaming (STREAM)
# ============================================================================

class Text4HDMI(BaseStreamConverter):
    """
    HDMI capture streaming.
    
    Funkcje:
    - Video capture
    - Frame grabbing
    - Resolution changes
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._port: int = 0
        self._resolution: str = "1920x1080"
        self._frame_count: int = 0
    
    async def connect(self, target: str) -> bool:
        """Połącz z HDMI capture"""
        try:
            self._port = int(target) if target.isdigit() else 0
            self.state = StreamState.CONNECTED
            logger.info(f"Connected to HDMI port: {self._port}")
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Konfiguracja capture"""
        if isinstance(data, dict):
            self._resolution = data.get("resolution", self._resolution)
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Odbiera klatki video"""
        
        self._frame_count += 1
        
        # Symulacja frame capture
        frame_data = {
            "frame_number": self._frame_count,
            "resolution": self._resolution,
            "timestamp": datetime.now().isoformat(),
            "size_bytes": 1920 * 1080 * 3  # RGB
        }
        
        await asyncio.sleep(1/60)  # 60 FPS
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="hdmi_frame",
            data=frame_data,
            source=f"hdmi://{self._port}",
            metadata={
                "port": self._port,
                "resolution": self._resolution
            }
        )


# ============================================================================
# Serial Port Converters
# ============================================================================

@dataclass
class SerialConfig:
    """Konfiguracja portu szeregowego"""
    port: str
    baudrate: int = 9600
    bytesize: int = 8
    parity: str = 'N'  # N, E, O
    stopbits: float = 1
    timeout: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "bytesize": self.bytesize,
            "parity": self.parity,
            "stopbits": self.stopbits,
            "timeout": self.timeout
        }


# ============================================================================
# text2serial - Read Serial (READ)
# ============================================================================

class Text2Serial(BaseConverter):
    """
    Czytnik portu szeregowego.
    
    Funkcje:
    - Odczyt danych
    - Listowanie portów
    - Konfiguracja
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę serial"""
        return f"serial_{intent.get('action', 'read')}"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję serial"""
        text = text.lower()
        
        action = "read"
        if "list" in text or "porty" in text:
            action = "list"
        elif "config" in text or "konfigur" in text:
            action = "config"
        
        # Port
        port_match = re.search(r'(com\d+|/dev/tty\w+)', text, re.IGNORECASE)
        port = port_match.group(1) if port_match else "/dev/ttyUSB0"
        
        # Baudrate
        baud_match = re.search(r'(\d+)\s*(?:baud|bps)?', text)
        baudrate = int(baud_match.group(1)) if baud_match and int(baud_match.group(1)) in [9600, 19200, 38400, 57600, 115200] else 9600
        
        return {
            "action": action,
            "port": port,
            "baudrate": baudrate,
            "description": text
        }
    
    def list_ports(self) -> List[Dict]:
        """Listuje porty szeregowe (symulacja)"""
        
        return [
            {"port": "/dev/ttyUSB0", "description": "USB-Serial Adapter"},
            {"port": "/dev/ttyACM0", "description": "Arduino Uno"},
            {"port": "/dev/ttyS0", "description": "COM1"},
        ]
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje operację serial"""
        
        try:
            intent = self.parse_intent(text)
            
            if intent["action"] == "list":
                ports = self.list_ports()
                output = "\n".join([f"{p['port']} - {p['description']}" for p in ports])
                
                return ConversionResult(
                    success=True,
                    command="ls /dev/tty*",
                    output=output,
                    metadata={"action": "list", "ports": ports}
                )
            
            elif intent["action"] == "read":
                # Symulacja odczytu
                import random
                data = f"Sensor value: {random.uniform(20, 30):.2f}"
                
                return ConversionResult(
                    success=True,
                    command=f"cat {intent['port']}",
                    output=data,
                    metadata={
                        "action": "read",
                        "port": intent["port"],
                        "baudrate": intent["baudrate"]
                    }
                )
            
            else:
                return ConversionResult(
                    success=False,
                    error="Unknown action"
                )
                
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3serial - Write Serial (WRITE)
# ============================================================================

class Text3Serial(BaseConverter):
    """
    Zapisywacz portu szeregowego.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę serial"""
        return "serial_write"
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję zapisu serial"""
        
        # Port
        port_match = re.search(r'(com\d+|/dev/tty\w+)', text.lower(), re.IGNORECASE)
        port = port_match.group(1) if port_match else "/dev/ttyUSB0"
        
        # Data
        data_match = re.search(r'(?:data|send|wyślij)[:\s]+["\']?([^"\']+)["\']?', text.lower())
        data = data_match.group(1) if data_match else "test"
        
        return {
            "port": port,
            "data": data,
            "description": text
        }
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje zapis serial"""
        
        try:
            intent = self.parse_intent(text)
            
            return ConversionResult(
                success=True,
                command=f"echo '{intent['data']}' > {intent['port']}",
                output=f"Sent '{intent['data']}' to {intent['port']}",
                metadata={
                    "port": intent["port"],
                    "data": intent["data"],
                    "bytes_sent": len(intent["data"])
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4serial - Serial Streaming (STREAM)
# ============================================================================

class Text4Serial(BaseStreamConverter):
    """
    Serial port streaming.
    
    Funkcje:
    - Continuous monitoring
    - Line-by-line reading
    - Data logging
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self._serial_config: SerialConfig = None
        self._line_count: int = 0
    
    async def connect(self, target: str) -> bool:
        """Połącz z portem szeregowym"""
        try:
            # Parse: /dev/ttyUSB0:9600 or just /dev/ttyUSB0
            if ':' in target:
                port, baud = target.rsplit(':', 1)
                baudrate = int(baud)
            else:
                port = target
                baudrate = 9600
            
            self._serial_config = SerialConfig(port=port, baudrate=baudrate)
            self.state = StreamState.CONNECTED
            logger.info(f"Connected to serial port: {port} @ {baudrate}")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self._serial_config = None
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Wyślij dane przez port szeregowy"""
        logger.info(f"Sending to serial: {data}")
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Odbiera dane z portu szeregowego"""
        
        self._line_count += 1
        
        import random
        
        # Symulacja danych sensorowych
        data_types = [
            f"T:{random.uniform(20, 30):.1f}",
            f"H:{random.uniform(40, 70):.1f}",
            f"P:{random.uniform(990, 1030):.1f}",
            f"OK",
            f"ERROR:{random.randint(1, 10)}"
        ]
        
        line = random.choice(data_types)
        
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="serial_data",
            data={
                "line": line,
                "line_number": self._line_count,
                "port": self._serial_config.port if self._serial_config else "unknown"
            },
            source=f"serial://{self._serial_config.port if self._serial_config else 'unknown'}",
            metadata={
                "baudrate": self._serial_config.baudrate if self._serial_config else 0
            }
        )

# Patch: Add missing generate_command methods  
Text2USB.generate_command = lambda self, intent: f"usb_{intent.get('action', 'list')}"
Text3USB.generate_command = lambda self, intent: f"usb_{intent.get('action', 'write')}"
Text2HDMI.generate_command = lambda self, intent: f"hdmi_{intent.get('action', 'info')}"
Text2Serial.generate_command = lambda self, intent: f"serial_{intent.get('action', 'read')}"
Text3Serial.generate_command = lambda self, intent: f"serial_write"

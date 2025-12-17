"""
Industrial Protocol Converters - Modbus & MQTT

text2modbus, text3modbus, text4modbus - Modbus TCP/RTU
text2mqtt, text3mqtt, text4mqtt - MQTT messaging
"""

from typing import Dict, Any, Optional, List, Union
from nlp2cmd.core.base import BaseConverter, ConversionResult
from nlp2cmd.core.stream_base import BaseStreamConverter, StreamEvent, StreamConfig, StreamState
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import struct
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Modbus Data Types
# ============================================================================

class ModbusFunction(Enum):
    """Funkcje Modbus"""
    READ_COILS = 0x01
    READ_DISCRETE_INPUTS = 0x02
    READ_HOLDING_REGISTERS = 0x03
    READ_INPUT_REGISTERS = 0x04
    WRITE_SINGLE_COIL = 0x05
    WRITE_SINGLE_REGISTER = 0x06
    WRITE_MULTIPLE_COILS = 0x0F
    WRITE_MULTIPLE_REGISTERS = 0x10


@dataclass
class ModbusRequest:
    """Żądanie Modbus"""
    slave_id: int
    function: ModbusFunction
    address: int
    count: int = 1
    values: List[int] = None
    
    def to_bytes(self) -> bytes:
        """Konwertuje do bajtów (Modbus TCP)"""
        # Transaction ID (2) + Protocol ID (2) + Length (2) + Unit ID (1) + Function (1) + Data
        data = struct.pack('>BB', self.slave_id, self.function.value)
        data += struct.pack('>HH', self.address, self.count)
        
        # Header
        length = len(data)
        header = struct.pack('>HHHB', 0, 0, length + 1, self.slave_id)
        
        return header + data[1:]


@dataclass
class ModbusResponse:
    """Odpowiedź Modbus"""
    slave_id: int
    function: ModbusFunction
    data: bytes
    values: List[int] = None
    error: str = None
    
    @classmethod
    def parse(cls, raw: bytes) -> 'ModbusResponse':
        """Parsuje odpowiedź"""
        if len(raw) < 8:
            return cls(0, ModbusFunction.READ_HOLDING_REGISTERS, b'', error="Invalid response")
        
        # Skip MBAP header (7 bytes for TCP)
        unit_id = raw[6]
        function = raw[7]
        
        if function & 0x80:  # Error
            return cls(unit_id, ModbusFunction(function & 0x7F), raw, error=f"Modbus error: {raw[8]}")
        
        # Parse based on function
        if function in [0x01, 0x02]:  # Coils / Discrete inputs
            byte_count = raw[8]
            values = list(raw[9:9+byte_count])
        elif function in [0x03, 0x04]:  # Registers
            byte_count = raw[8]
            values = []
            for i in range(9, 9 + byte_count, 2):
                values.append(struct.unpack('>H', raw[i:i+2])[0])
        else:
            values = []
        
        return cls(unit_id, ModbusFunction(function), raw, values=values)


# ============================================================================
# text2modbus - Read Modbus (READ)
# ============================================================================

class Text2Modbus(BaseConverter):
    def generate_command(self, intent):
        return f"modbus_read"

    """
    Czytnik Modbus.
    
    Funkcje:
    - Odczyt rejestrów holding
    - Odczyt rejestrów input
    - Odczyt coils
    - Parsowanie danych
    """
    
    def __init__(self, host: str = "localhost", port: int = 502, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję odczytu Modbus"""
        text = text.lower()
        
        # Detect function
        function = ModbusFunction.READ_HOLDING_REGISTERS
        if "coil" in text:
            function = ModbusFunction.READ_COILS
        elif "discrete" in text or "input" in text and "register" not in text:
            function = ModbusFunction.READ_DISCRETE_INPUTS
        elif "input" in text and "register" in text:
            function = ModbusFunction.READ_INPUT_REGISTERS
        
        # Extract address
        addr_match = re.search(r'(?:address|adres|rejestr)\s*[=:]?\s*(\d+)', text)
        address = int(addr_match.group(1)) if addr_match else 0
        
        # Alternative: 40001 format (Modbus convention)
        modbus_addr = re.search(r'\b([0134]\d{4})\b', text)
        if modbus_addr:
            addr_str = modbus_addr.group(1)
            if addr_str.startswith('0'):
                function = ModbusFunction.READ_COILS
                address = int(addr_str) - 1
            elif addr_str.startswith('1'):
                function = ModbusFunction.READ_DISCRETE_INPUTS
                address = int(addr_str) - 10001
            elif addr_str.startswith('3'):
                function = ModbusFunction.READ_INPUT_REGISTERS
                address = int(addr_str) - 30001
            elif addr_str.startswith('4'):
                function = ModbusFunction.READ_HOLDING_REGISTERS
                address = int(addr_str) - 40001
        
        # Extract count
        count_match = re.search(r'(?:count|ilość|liczba)\s*[=:]?\s*(\d+)', text)
        count = int(count_match.group(1)) if count_match else 1
        
        # Extract slave ID
        slave_match = re.search(r'(?:slave|unit|jednostka)\s*[=:]?\s*(\d+)', text)
        slave_id = int(slave_match.group(1)) if slave_match else 1
        
        return {
            "function": function,
            "address": address,
            "count": count,
            "slave_id": slave_id,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę Modbus"""
        
        func_names = {
            ModbusFunction.READ_COILS: "Read Coils",
            ModbusFunction.READ_DISCRETE_INPUTS: "Read Discrete Inputs",
            ModbusFunction.READ_HOLDING_REGISTERS: "Read Holding Registers",
            ModbusFunction.READ_INPUT_REGISTERS: "Read Input Registers"
        }
        
        return f"{func_names[intent['function']]} @ {intent['address']} x {intent['count']} (Slave {intent['slave_id']})"
    
    def simulate_read(self, intent: Dict[str, Any]) -> ModbusResponse:
        """Symuluje odczyt Modbus (do testów)"""
        
        import random
        
        if intent['function'] in [ModbusFunction.READ_COILS, ModbusFunction.READ_DISCRETE_INPUTS]:
            # Binary values
            values = [random.randint(0, 1) for _ in range(intent['count'])]
        else:
            # Register values
            values = [random.randint(0, 65535) for _ in range(intent['count'])]
        
        return ModbusResponse(
            slave_id=intent['slave_id'],
            function=intent['function'],
            data=b'',
            values=values
        )
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje odczyt Modbus"""
        
        try:
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            # Simulate read (w produkcji: prawdziwe połączenie TCP)
            response = self.simulate_read(intent)
            
            if response.error:
                return ConversionResult(
                    success=False,
                    error=response.error,
                    metadata={"intent": intent}
                )
            
            return ConversionResult(
                success=True,
                command=command,
                output=str(response.values),
                metadata={
                    "function": intent['function'].name,
                    "address": intent['address'],
                    "count": intent['count'],
                    "slave_id": intent['slave_id'],
                    "values": response.values
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3modbus - Write Modbus (WRITE)
# ============================================================================

class Text3Modbus(BaseConverter):
    def generate_command(self, intent):
        return f"modbus_write"

    """
    Zapisywacz Modbus.
    
    Funkcje:
    - Zapis do rejestrów
    - Zapis do coils
    - Konfiguracja urządzeń
    """
    
    def __init__(self, host: str = "localhost", port: int = 502, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję zapisu Modbus"""
        text = text.lower()
        
        # Detect function
        function = ModbusFunction.WRITE_SINGLE_REGISTER
        if "coil" in text:
            function = ModbusFunction.WRITE_SINGLE_COIL
        elif "multiple" in text or "wiele" in text:
            if "coil" in text:
                function = ModbusFunction.WRITE_MULTIPLE_COILS
            else:
                function = ModbusFunction.WRITE_MULTIPLE_REGISTERS
        
        # Extract address
        addr_match = re.search(r'(?:address|adres|rejestr)\s*[=:]?\s*(\d+)', text)
        address = int(addr_match.group(1)) if addr_match else 0
        
        # Extract value(s)
        value_match = re.search(r'(?:value|wartość|ustaw)\s*[=:]?\s*(\d+)', text)
        values = [int(value_match.group(1))] if value_match else [0]
        
        # Multiple values
        multi_match = re.search(r'values?\s*[=:]?\s*\[([^\]]+)\]', text)
        if multi_match:
            values = [int(v.strip()) for v in multi_match.group(1).split(',')]
        
        # Slave ID
        slave_match = re.search(r'(?:slave|unit)\s*[=:]?\s*(\d+)', text)
        slave_id = int(slave_match.group(1)) if slave_match else 1
        
        return {
            "function": function,
            "address": address,
            "values": values,
            "slave_id": slave_id,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę zapisu"""
        
        func_names = {
            ModbusFunction.WRITE_SINGLE_COIL: "Write Single Coil",
            ModbusFunction.WRITE_SINGLE_REGISTER: "Write Single Register",
            ModbusFunction.WRITE_MULTIPLE_COILS: "Write Multiple Coils",
            ModbusFunction.WRITE_MULTIPLE_REGISTERS: "Write Multiple Registers"
        }
        
        return f"{func_names[intent['function']]} @ {intent['address']} = {intent['values']}"
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje zapis Modbus"""
        
        try:
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            # W produkcji: prawdziwy zapis
            # Tutaj: symulacja sukcesu
            
            return ConversionResult(
                success=True,
                command=command,
                output=f"Written {intent['values']} to address {intent['address']}",
                metadata={
                    "function": intent['function'].name,
                    "address": intent['address'],
                    "values": intent['values'],
                    "slave_id": intent['slave_id']
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4modbus - Continuous Modbus Monitoring (STREAM)
# ============================================================================

class Text4Modbus(BaseStreamConverter):
    """
    Ciągłe monitorowanie Modbus.
    
    Funkcje:
    - Polling rejestrów
    - Event-driven updates
    - Data logging
    - Alerting
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self.host = "localhost"
        self.port = 502
        self._polling_config: Dict[str, Any] = {}
        self._reader = Text2Modbus()
    
    async def connect(self, target: str) -> bool:
        """
        Połącz z urządzeniem Modbus.
        
        Args:
            target: "host:port" (np. "192.168.1.100:502")
        """
        try:
            if ':' in target:
                self.host, port_str = target.split(':')
                self.port = int(port_str)
            else:
                self.host = target
            
            self._reader.host = self.host
            self._reader.port = self.port
            
            self.state = StreamState.CONNECTED
            logger.info(f"Connected to Modbus device: {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.state = StreamState.ERROR
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Konfiguruje polling"""
        if isinstance(data, dict):
            self._polling_config = data
        return True
    
    async def receive(self) -> Optional[StreamEvent]:
        """Odczytuje dane z urządzenia"""
        
        # Default polling: read holding registers 0-9
        config = self._polling_config or {
            "function": "READ_HOLDING_REGISTERS",
            "address": 0,
            "count": 10,
            "slave_id": 1
        }
        
        intent = {
            "function": ModbusFunction[config.get("function", "READ_HOLDING_REGISTERS")],
            "address": config.get("address", 0),
            "count": config.get("count", 10),
            "slave_id": config.get("slave_id", 1)
        }
        
        response = self._reader.simulate_read(intent)
        
        # Poll interval
        poll_interval = config.get("interval", 1.0)
        await asyncio.sleep(poll_interval)
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="modbus_read",
            data={
                "address": intent["address"],
                "values": response.values,
                "function": intent["function"].name
            },
            source=f"text4modbus://{self.host}:{self.port}",
            metadata={
                "slave_id": intent["slave_id"],
                "count": intent["count"]
            }
        )
    
    def configure_polling(
        self,
        address: int,
        count: int = 1,
        interval: float = 1.0,
        function: str = "READ_HOLDING_REGISTERS"
    ):
        """Konfiguruje polling"""
        self._polling_config = {
            "address": address,
            "count": count,
            "interval": interval,
            "function": function
        }


# ============================================================================
# MQTT Converters
# ============================================================================

@dataclass
class MQTTMessage:
    """Wiadomość MQTT"""
    topic: str
    payload: Union[str, bytes]
    qos: int = 0
    retain: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


# ============================================================================
# text2mqtt - Subscribe/Receive MQTT (READ)
# ============================================================================

class Text2MQTT(BaseConverter):
    def generate_command(self, intent):
        return f"mqtt_{intent.get('action', 'subscribe')}"

    """
    Odbiorca MQTT.
    
    Funkcje:
    - Subskrypcja topicow
    - Odbiór wiadomości
    - Pattern matching
    """
    
    def __init__(self, broker: str = "localhost", port: int = 1883, **kwargs):
        super().__init__(**kwargs)
        self.broker = broker
        self.port = port
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję MQTT"""
        text = text.lower()
        
        action = "subscribe"
        if "publish" in text or "wyślij" in text:
            action = "publish"
        elif "list" in text or "topics" in text:
            action = "list_topics"
        
        # Extract topic
        topic_match = re.search(r'topic[:\s]+["\']?([^"\']+)["\']?', text)
        topic = topic_match.group(1).strip() if topic_match else "#"
        
        # Alternative patterns
        if "sensors" in text:
            topic = "sensors/#"
        elif "devices" in text:
            topic = "devices/#"
        elif "home" in text:
            topic = "home/#"
        
        # Extract message for publish
        msg_match = re.search(r'(?:message|wiadomość)[:\s]+["\']?([^"\']+)["\']?', text)
        message = msg_match.group(1).strip() if msg_match else None
        
        return {
            "action": action,
            "topic": topic,
            "message": message,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje komendę MQTT"""
        
        if intent["action"] == "subscribe":
            return f"SUBSCRIBE {intent['topic']}"
        elif intent["action"] == "publish":
            return f"PUBLISH {intent['topic']} '{intent['message']}'"
        else:
            return "LIST TOPICS"
    
    def execute(self, text: str) -> ConversionResult:
        """Wykonuje operację MQTT"""
        
        try:
            intent = self.parse_intent(text)
            command = self.generate_command(intent)
            
            # Simulation
            if intent["action"] == "subscribe":
                output = f"Subscribed to: {intent['topic']}"
            elif intent["action"] == "publish":
                output = f"Published to {intent['topic']}: {intent['message']}"
            else:
                output = "Topics: sensors/#, devices/#, home/#"
            
            return ConversionResult(
                success=True,
                command=command,
                output=output,
                metadata={
                    "action": intent["action"],
                    "topic": intent["topic"],
                    "broker": f"{self.broker}:{self.port}"
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text3mqtt - Publish MQTT (WRITE)
# ============================================================================

class Text3MQTT(BaseConverter):
    def generate_command(self, intent):
        return f"mqtt_publish_{intent.get('topic', 'default')}"

    """
    Nadawca MQTT.
    
    Funkcje:
    - Publikowanie wiadomości
    - QoS configuration
    - Retain messages
    """
    
    def __init__(self, broker: str = "localhost", port: int = 1883, **kwargs):
        super().__init__(**kwargs)
        self.broker = broker
        self.port = port
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """Parsuje intencję publikacji"""
        
        # Topic
        topic_match = re.search(r'topic[:\s]+["\']?([^"\']+)["\']?', text.lower())
        topic = topic_match.group(1).strip() if topic_match else "default/topic"
        
        # Message
        msg_match = re.search(r'(?:message|payload|dane)[:\s]+["\']?([^"\']+)["\']?', text.lower())
        message = msg_match.group(1).strip() if msg_match else text
        
        # QoS
        qos = 0
        if "qos 1" in text.lower() or "at least once" in text.lower():
            qos = 1
        elif "qos 2" in text.lower() or "exactly once" in text.lower():
            qos = 2
        
        # Retain
        retain = "retain" in text.lower()
        
        return {
            "topic": topic,
            "message": message,
            "qos": qos,
            "retain": retain
        }
    
    def execute(self, text: str) -> ConversionResult:
        """Publikuje wiadomość MQTT"""
        
        try:
            intent = self.parse_intent(text)
            
            # W produkcji: prawdziwa publikacja
            # Tutaj: symulacja
            
            return ConversionResult(
                success=True,
                command=f"PUBLISH {intent['topic']}",
                output=f"Published to {intent['topic']}: {intent['message']} (QoS={intent['qos']}, Retain={intent['retain']})",
                metadata={
                    "topic": intent["topic"],
                    "message": intent["message"],
                    "qos": intent["qos"],
                    "retain": intent["retain"],
                    "broker": f"{self.broker}:{self.port}"
                }
            )
            
        except Exception as e:
            return ConversionResult(success=False, error=str(e))


# ============================================================================
# text4mqtt - MQTT Streaming (STREAM)
# ============================================================================

class Text4MQTT(BaseStreamConverter):
    """
    MQTT streaming.
    
    Funkcje:
    - Ciągła subskrypcja
    - Multi-topic monitoring
    - Message filtering
    - Event callbacks
    """
    
    def __init__(self, config: StreamConfig = None):
        super().__init__(config)
        self.broker = "localhost"
        self.port = 1883
        self._subscriptions: List[str] = []
        self._message_count = 0
    
    async def connect(self, target: str) -> bool:
        """
        Połącz z brokerem MQTT.
        
        Args:
            target: "mqtt://host:port" lub "host:port"
        """
        try:
            target = target.replace("mqtt://", "")
            
            if ':' in target:
                self.broker, port_str = target.split(':')
                self.port = int(port_str)
            else:
                self.broker = target
            
            self.state = StreamState.CONNECTED
            logger.info(f"Connected to MQTT broker: {self.broker}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Rozłącz"""
        self._subscriptions = []
        self.state = StreamState.DISCONNECTED
        return True
    
    async def send(self, data: Any) -> bool:
        """Publikuj wiadomość"""
        if isinstance(data, MQTTMessage):
            logger.info(f"Publishing to {data.topic}")
            return True
        elif isinstance(data, dict):
            logger.info(f"Publishing to {data.get('topic')}")
            return True
        return False
    
    async def receive(self) -> Optional[StreamEvent]:
        """Odbiera wiadomości MQTT"""
        
        self._message_count += 1
        
        # Symulacja wiadomości
        import random
        topics = self._subscriptions or ["sensors/temperature", "sensors/humidity", "devices/status"]
        
        topic = random.choice(topics)
        
        if "temperature" in topic:
            payload = {"value": random.uniform(18, 28), "unit": "°C"}
        elif "humidity" in topic:
            payload = {"value": random.uniform(40, 80), "unit": "%"}
        else:
            payload = {"status": random.choice(["online", "offline", "error"])}
        
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        return StreamEvent(
            timestamp=datetime.now(),
            event_type="mqtt_message",
            data={
                "topic": topic,
                "payload": payload,
                "qos": 0
            },
            source=f"mqtt://{self.broker}:{self.port}",
            metadata={
                "message_count": self._message_count
            }
        )
    
    def add_subscription(self, topic: str):
        """Dodaj subskrypcję"""
        if topic not in self._subscriptions:
            self._subscriptions.append(topic)
            logger.info(f"Subscribed to: {topic}")
    
    def remove_subscription(self, topic: str):
        """Usuń subskrypcję"""
        if topic in self._subscriptions:
            self._subscriptions.remove(topic)

# Patch: Add missing generate_command methods
Text3MQTT.generate_command = lambda self, intent: f"mqtt_publish_{intent.get('topic', 'default')}"
Text2MQTT.generate_command = lambda self, intent: f"mqtt_{intent.get('action', 'subscribe')}"
Text2Modbus.generate_command = lambda self, intent: f"modbus_read_{intent.get('function', 'holding').name}"
Text3Modbus.generate_command = lambda self, intent: f"modbus_write_{intent.get('function', 'register').name}"

"""
Base classes for text4X streaming converters.

text4X converters handle bidirectional, continuous communication
with devices, protocols, and services.
"""

from typing import Dict, Any, Optional, List, Callable, AsyncIterator
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class StreamState(Enum):
    """Stan streamu"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"
    CLOSING = "closing"


@dataclass
class StreamEvent:
    """Wydarzenie w streamie"""
    timestamp: datetime
    event_type: str
    data: Any
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "data": self.data,
            "source": self.source,
            "metadata": self.metadata
        }


@dataclass
class StreamConfig:
    """Konfiguracja streamu"""
    buffer_size: int = 1000
    timeout: float = 30.0
    reconnect: bool = True
    reconnect_delay: float = 5.0
    max_reconnect_attempts: int = 5
    heartbeat_interval: float = 10.0


class BaseStreamConverter(ABC):
    """
    Bazowa klasa dla text4X streaming converters.
    
    Obsługuje:
    - Bidirectional communication
    - Event streaming
    - Subscriptions
    - Automatic reconnection
    - Buffer management
    """
    
    def __init__(self, config: Optional[StreamConfig] = None):
        self.config = config or StreamConfig()
        self.state = StreamState.DISCONNECTED
        self._callbacks: List[Callable] = []
        self._buffer: List[StreamEvent] = []
        self._subscriptions: Dict[str, Callable] = {}
        self._connection = None
        self._running = False
        self._reconnect_count = 0
    
    @property
    def is_connected(self) -> bool:
        return self.state in [StreamState.CONNECTED, StreamState.STREAMING]
    
    @abstractmethod
    async def connect(self, target: str) -> bool:
        """
        Nawiąż połączenie z celem.
        
        Args:
            target: Adres/identyfikator celu (np. "192.168.1.100:502")
            
        Returns:
            True jeśli połączono
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Zamknij połączenie.
        
        Returns:
            True jeśli rozłączono
        """
        pass
    
    @abstractmethod
    async def send(self, data: Any) -> bool:
        """
        Wyślij dane.
        
        Args:
            data: Dane do wysłania
            
        Returns:
            True jeśli wysłano
        """
        pass
    
    @abstractmethod
    async def receive(self) -> Optional[StreamEvent]:
        """
        Odbierz dane.
        
        Returns:
            Wydarzenie lub None
        """
        pass
    
    def subscribe(self, pattern: str, callback: Callable[[StreamEvent], None]) -> str:
        """
        Subskrybuj na wzorzec.
        
        Args:
            pattern: Wzorzec do monitorowania
            callback: Funkcja wywoływana przy dopasowaniu
            
        Returns:
            ID subskrypcji
        """
        sub_id = f"sub_{len(self._subscriptions)}_{pattern}"
        self._subscriptions[sub_id] = {
            "pattern": pattern,
            "callback": callback
        }
        logger.info(f"Subscribed: {sub_id}")
        return sub_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Anuluj subskrypcję.
        
        Args:
            subscription_id: ID subskrypcji
            
        Returns:
            True jeśli anulowano
        """
        if subscription_id in self._subscriptions:
            del self._subscriptions[subscription_id]
            logger.info(f"Unsubscribed: {subscription_id}")
            return True
        return False
    
    def on_event(self, callback: Callable[[StreamEvent], None]):
        """
        Zarejestruj callback dla wszystkich wydarzeń.
        
        Args:
            callback: Funkcja wywoływana przy każdym wydarzeniu
        """
        self._callbacks.append(callback)
    
    async def stream(self) -> AsyncIterator[StreamEvent]:
        """
        Generator asynchroniczny dla eventów.
        
        Yields:
            StreamEvent z danymi
        """
        self._running = True
        
        while self._running:
            try:
                event = await self.receive()
                
                if event:
                    # Buffer event
                    self._buffer.append(event)
                    if len(self._buffer) > self.config.buffer_size:
                        self._buffer.pop(0)
                    
                    # Notify callbacks
                    for callback in self._callbacks:
                        try:
                            callback(event)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                    
                    # Check subscriptions
                    for sub_id, sub in self._subscriptions.items():
                        if self._matches_pattern(event, sub["pattern"]):
                            try:
                                sub["callback"](event)
                            except Exception as e:
                                logger.error(f"Subscription callback error: {e}")
                    
                    yield event
                
                else:
                    # No data, brief pause
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Stream error: {e}")
                
                if self.config.reconnect and self._reconnect_count < self.config.max_reconnect_attempts:
                    await self._attempt_reconnect()
                else:
                    self.state = StreamState.ERROR
                    break
    
    async def _attempt_reconnect(self):
        """Próba ponownego połączenia"""
        self._reconnect_count += 1
        logger.info(f"Reconnect attempt {self._reconnect_count}/{self.config.max_reconnect_attempts}")
        
        await asyncio.sleep(self.config.reconnect_delay)
        
        # Subclasses should implement actual reconnection
        self.state = StreamState.CONNECTING
    
    def _matches_pattern(self, event: StreamEvent, pattern: str) -> bool:
        """Sprawdza czy event pasuje do wzorca"""
        # Simple pattern matching - can be extended
        if pattern == "*":
            return True
        if pattern in str(event.data):
            return True
        if pattern == event.event_type:
            return True
        return False
    
    def stop(self):
        """Zatrzymaj streaming"""
        self._running = False
        self.state = StreamState.CLOSING
    
    def get_buffer(self) -> List[StreamEvent]:
        """Zwróć bufor wydarzeń"""
        return self._buffer.copy()
    
    def clear_buffer(self):
        """Wyczyść bufor"""
        self._buffer.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Zwróć statystyki streamu"""
        return {
            "state": self.state.value,
            "buffer_size": len(self._buffer),
            "subscriptions": len(self._subscriptions),
            "callbacks": len(self._callbacks),
            "reconnect_count": self._reconnect_count
        }


class StreamManager:
    """
    Manager dla wielu streamów.
    
    Pozwala zarządzać wieloma połączeniami text4X jednocześnie.
    """
    
    def __init__(self):
        self._streams: Dict[str, BaseStreamConverter] = {}
    
    def register(self, name: str, stream: BaseStreamConverter):
        """Zarejestruj stream"""
        self._streams[name] = stream
        logger.info(f"Registered stream: {name}")
    
    def get(self, name: str) -> Optional[BaseStreamConverter]:
        """Pobierz stream"""
        return self._streams.get(name)
    
    def remove(self, name: str):
        """Usuń stream"""
        if name in self._streams:
            del self._streams[name]
    
    async def connect_all(self, targets: Dict[str, str]) -> Dict[str, bool]:
        """Połącz wszystkie streamy"""
        results = {}
        
        for name, target in targets.items():
            stream = self._streams.get(name)
            if stream:
                results[name] = await stream.connect(target)
        
        return results
    
    async def disconnect_all(self):
        """Rozłącz wszystkie"""
        for stream in self._streams.values():
            await stream.disconnect()
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Statystyki wszystkich streamów"""
        return {
            name: stream.get_stats()
            for name, stream in self._streams.items()
        }

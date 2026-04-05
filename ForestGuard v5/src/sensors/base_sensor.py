"""
Base class for all sensor implementations.
"""
import threading
from abc import ABC, abstractmethod

class BaseSensor(ABC):
    """Base class that all sensors should inherit from."""
    
    def __init__(self, zone: str):
        """Initialize the sensor with a zone."""
        self.zone = zone
        self.running = False
        self.lock = threading.Lock()
        
    @abstractmethod
    def start_monitoring(self):
        """Start the sensor's monitoring loop."""
        pass
        
    def stop(self):
        """Stop the sensor's monitoring loop."""
        with self.lock:
            self.running = False
    
    def __str__(self):
        """String representation of the sensor."""
        return f"{self.__class__.__name__}(zone={self.zone})"

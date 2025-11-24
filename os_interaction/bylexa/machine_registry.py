"""
Machine Registry Module for Bylexa
Handles machine registration and capability reporting for the room system.
"""

import platform
import psutil
import socket
import uuid
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class MachineRegistry:
    """
    Manages machine information and capabilities for the Bylexa system.
    """

    def __init__(self):
        """Initialize the machine registry."""
        self.machine_id = None
        self.machine_data = {}
        self._generate_machine_info()

    def _generate_machine_info(self):
        """Generate comprehensive machine information."""
        try:
            # Generate a unique machine ID based on hostname and MAC address
            mac = uuid.getnode()
            hostname = socket.gethostname()
            self.machine_id = f"{hostname}-{mac}"

            # Collect system information
            self.machine_data = {
                'os': platform.system(),
                'platform': platform.platform(),
                'hostname': hostname,
                'processor': platform.processor(),
                'architecture': platform.machine(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_total': psutil.disk_usage('/').total if hasattr(psutil.disk_usage('/'), 'total') else 0,
                'disk_free': psutil.disk_usage('/').free if hasattr(psutil.disk_usage('/'), 'free') else 0,
                'capabilities': self._detect_capabilities()
            }

            logger.info(f"Machine ID generated: {self.machine_id}")
            logger.info(f"Machine data collected: {self.machine_data}")

        except Exception as e:
            logger.error(f"Error generating machine info: {str(e)}")
            # Fallback to basic info
            self.machine_id = f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"
            self.machine_data = {
                'os': platform.system(),
                'platform': platform.platform(),
                'hostname': socket.gethostname(),
                'capabilities': []
            }

    def _detect_capabilities(self) -> List[str]:
        """
        Detect machine capabilities (what it can do).

        Returns:
            List of capability strings
        """
        capabilities = []

        # Python execution
        capabilities.append('python')

        # OS-specific capabilities
        if platform.system() == 'Windows':
            capabilities.extend(['windows', 'powershell', 'cmd'])
        elif platform.system() == 'Linux':
            capabilities.extend(['linux', 'bash', 'sh'])
        elif platform.system() == 'Darwin':
            capabilities.extend(['macos', 'bash', 'zsh'])

        # Check for common tools
        try:
            import selenium
            capabilities.append('selenium')
        except ImportError:
            pass

        try:
            import numpy
            capabilities.append('numpy')
        except ImportError:
            pass

        try:
            import pandas
            capabilities.append('pandas')
        except ImportError:
            pass

        try:
            import tensorflow
            capabilities.append('tensorflow')
        except ImportError:
            pass

        try:
            import torch
            capabilities.append('pytorch')
        except ImportError:
            pass

        # Check if GPU is available
        try:
            import torch
            if torch.cuda.is_available():
                capabilities.append('cuda')
                capabilities.append('gpu')
        except ImportError:
            pass

        return capabilities

    def get_machine_id(self) -> str:
        """
        Get the unique machine ID.

        Returns:
            Machine ID string
        """
        return self.machine_id

    def get_machine_data(self) -> Dict[str, Any]:
        """
        Get the complete machine data.

        Returns:
            Dictionary with machine information
        """
        return self.machine_data

    def get_registration_message(self) -> Dict[str, Any]:
        """
        Get the registration message to send to the server.

        Returns:
            Dictionary with registration data
        """
        return {
            'action': 'register_machine',
            'machine_id': self.machine_id,
            'machine_data': self.machine_data
        }

    def update_capabilities(self):
        """Update machine capabilities (useful if new packages are installed)."""
        self.machine_data['capabilities'] = self._detect_capabilities()
        logger.info(f"Updated capabilities: {self.machine_data['capabilities']}")

    def get_current_resources(self) -> Dict[str, Any]:
        """
        Get current resource usage.

        Returns:
            Dictionary with current resource information
        """
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'memory_available': psutil.virtual_memory().available,
                'disk_percent': psutil.disk_usage('/').percent,
                'disk_free': psutil.disk_usage('/').free
            }
        except Exception as e:
            logger.error(f"Error getting current resources: {str(e)}")
            return {}


# Singleton instance
_registry_instance = None


def get_machine_registry() -> MachineRegistry:
    """
    Get the global machine registry instance.

    Returns:
        MachineRegistry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = MachineRegistry()
    return _registry_instance

"""Device module for Android device interactions"""

from typing import Dict, List, Optional
from pathlib import Path

from .utils.adb import AndroidDevice
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class Device:
    """Class to handle Android device interactions"""
    
    def __init__(self):
        """Initialize Android device handler"""
        self.device = AndroidDevice()
        self._device_info = self.device.get_device_info()
        logger.info(f"Connected to {self._device_info.get('manufacturer', 'Unknown')} {self._device_info.get('model', 'Unknown')} running Android {self._device_info.get('android_version', 'Unknown')}")
    
    def get_installed_apps(self) -> List[str]:
        """Get list of installed apps"""
        apps = self.device.get_installed_apps()
        logger.debug(f"Found {len(apps)} installed apps")
        return apps
    
    def get_app_details(self, package_id: str) -> Dict:
        """Get detailed information about an app"""
        return self.device.get_app_details(package_id)
    
    def get_device_info(self) -> Dict:
        """Get device information"""
        return self._device_info
    
    @property
    def manufacturer(self) -> str:
        """Get device manufacturer"""
        return self._device_info.get('manufacturer', 'Unknown')
    
    @property
    def model(self) -> str:
        """Get device model"""
        return self._device_info.get('model', 'Unknown')
    
    @property
    def android_version(self) -> str:
        """Get Android version"""
        return self._device_info.get('android_version', 'Unknown')
    
    @property
    def identifiers(self) -> Dict:
        """Get device identifiers"""
        return self._device_info.get('identifiers', {})

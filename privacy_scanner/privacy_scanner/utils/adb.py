import subprocess
from typing import Dict, List, Optional
from pathlib import Path
import re

from .logger import setup_logger

logger = setup_logger(__name__)

class AndroidDevice:
    """Class to interact with an Android device via ADB"""
    
    def __init__(self):
        """Initialize the Android device connection"""
        if not self.check_adb():
            raise RuntimeError("ADB not available or no device connected")
    
    def check_adb(self) -> bool:
        """Check if ADB is installed and a device is connected"""
        try:
            version_cmd = subprocess.run(['adb', 'version'], 
                                       capture_output=True, 
                                       text=True)
            if version_cmd.returncode != 0:
                logger.error("ADB is not installed")
                return False
                
            devices_cmd = subprocess.run(['adb', 'devices'], 
                                       capture_output=True, 
                                       text=True)
            devices = devices_cmd.stdout.strip().split('\n')[1:]
            if not devices or all(line.strip() == '' for line in devices):
                logger.error("No Android devices connected")
                return False
                
            return True
            
        except FileNotFoundError:
            logger.error("ADB is not installed")
            return False
    
    def get_installed_apps(self) -> List[str]:
        """Get list of installed apps using ADB"""
        logger.info("Getting installed apps...")
        cmd = ['adb', 'shell', 'pm', 'list', 'packages']
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Failed to get installed apps")
            raise RuntimeError("ADB command failed")
            
        return [pkg.replace('package:', '').strip() 
                for pkg in result.stdout.strip().split('\n') 
                if pkg.strip()]
    
    def get_app_details(self, package_id: str) -> Dict:
        """Get detailed information about an app using pm dump"""
        cmd = ['adb', 'shell', 'pm', 'dump', package_id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Failed to get details for {package_id}")
            raise RuntimeError(f"ADB command failed for {package_id}")
        
        details = {
            'package_id': package_id,
            'app_name': package_id,  # Use package_id as default
            'permissions': {
                'requested': [],
                'granted': [],
                'denied': []
            },
            'install_source': None,
            'first_install_time': None,
            'last_update_time': None,
            'network_permissions': [],
            'shared_libraries': [],
            'shared_user_ids': []
        }
        
        current_section = None
        for line in result.stdout.split('\n'):
            line = line.strip()
            
            # Get app name - handle multiple formats
            if 'applicationInfo' in line:
                # Try to extract label in different formats
                if 'label=' in line:
                    try:
                        # Try standard format
                        label_part = line.split('label=')[1]
                        # Handle quoted labels
                        if '"' in label_part:
                            details['app_name'] = label_part.split('"')[1]
                        else:
                            # Handle unquoted labels
                            details['app_name'] = label_part.split()[0]
                    except (IndexError, Exception) as e:
                        logger.warning(f"Could not extract app name from label: {line}")
                        # Keep using package_id as fallback
                
            # Get install source
            elif 'installInitiator:' in line:
                details['install_source'] = line.split('installInitiator:')[1].strip()
                
            # Get install times
            elif 'firstInstallTime=' in line:
                details['first_install_time'] = line.split('firstInstallTime=')[1].split(' ')[0]
            elif 'lastUpdateTime=' in line:
                details['last_update_time'] = line.split('lastUpdateTime=')[1].split(' ')[0]
                
            # Track permissions sections
            elif 'requested permissions:' in line:
                current_section = 'requested'
            elif 'runtime permissions:' in line:
                current_section = 'runtime'
            elif 'install permissions:' in line:
                current_section = 'install'
            
            # Parse permissions
            elif current_section == 'requested' and line.startswith('android.permission.'):
                details['permissions']['requested'].append(line.strip())
            elif current_section == 'runtime' and 'granted=true' in line:
                perm = line.split(':')[0].strip()
                details['permissions']['granted'].append(perm)
            elif current_section == 'runtime' and 'granted=false' in line:
                perm = line.split(':')[0].strip()
                details['permissions']['denied'].append(perm)
                
            # Get network permissions
            elif 'INTERNET' in line or 'NETWORK' in line:
                details['network_permissions'].append(line.strip())
                
            # Get shared libraries
            elif 'libraryInfo' in line:
                details['shared_libraries'].append(line.strip())
                
            # Get shared user IDs
            elif 'sharedUser=' in line:
                details['shared_user_ids'].append(line.split('sharedUser=')[1].strip())
        
        return details
    
    def get_device_info(self) -> Dict[str, str]:
        """Get device manufacturer, model, and other details including unique identifiers"""
        info = {
            'manufacturer': None,
            'model': None,
            'brand': None,
            'device': None,
            'android_version': None,
            'security_patch': None,
            'identifiers': {
                'android_id': None,     # Android ID - Resets on factory reset
                'serial': None,        # Hardware serial number
                'mac_bluetooth': None, # Bluetooth MAC address
                'ip_addresses': []     # Current IP addresses (both WiFi and cellular)
            }
        }
        
        try:
            # Get device properties
            cmd = ['adb', 'shell', 'getprop']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                props = result.stdout.split('\n')
                for prop in props:
                    try:
                        if '[ro.product.manufacturer]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['manufacturer'] = match.group(2) if match else 'Unknown'
                        elif '[ro.product.model]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['model'] = match.group(2) if match else 'Unknown'
                        elif '[ro.product.brand]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['brand'] = match.group(2) if match else 'Unknown'
                        elif '[ro.product.device]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['device'] = match.group(2) if match else 'Unknown'
                        elif '[ro.build.version.release]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['android_version'] = match.group(2) if match else 'Unknown'
                        elif '[ro.build.version.security_patch]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['security_patch'] = match.group(2) if match else 'Unknown'
                        elif '[ro.serialno]' in prop:
                            match = re.search(r'\[(.*?)\]: \[(.*?)\]', prop)
                            info['identifiers']['serial'] = match.group(2) if match else 'Unknown'
                    except (AttributeError, IndexError) as e:
                        logger.warning(f"Failed to parse property: {prop} - {str(e)}")
            
            # Get Android ID (unique identifier that persists until factory reset)
            android_id_cmd = ['adb', 'shell', 'settings', 'get', 'secure', 'android_id']
            android_id_result = subprocess.run(android_id_cmd, capture_output=True, text=True)
            if android_id_result.returncode == 0:
                info['identifiers']['android_id'] = android_id_result.stdout.strip()
            
            # Get Bluetooth MAC address
            bt_mac_cmd = ['adb', 'shell', 'settings', 'get', 'secure', 'bluetooth_address']
            bt_result = subprocess.run(bt_mac_cmd, capture_output=True, text=True)
            if bt_result.returncode == 0:
                mac = bt_result.stdout.strip()
                if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                    info['identifiers']['mac_bluetooth'] = mac
            
            # Get IP addresses
            ip_cmd = ['adb', 'shell', 'ip', 'addr', 'show']
            ip_result = subprocess.run(ip_cmd, capture_output=True, text=True)
            if ip_result.returncode == 0:
                # Find all IPv4 addresses
                ip_matches = re.finditer(r'inet (\d+\.\d+\.\d+\.\d+)/', ip_result.stdout)
                for match in ip_matches:
                    ip = match.group(1)
                    if ip != '127.0.0.1':  # Exclude localhost
                        info['identifiers']['ip_addresses'].append(ip)
                        
        except Exception as e:
            logger.error(f"Failed to get device info: {str(e)}")
        
        return info 
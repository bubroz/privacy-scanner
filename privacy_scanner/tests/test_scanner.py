import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import subprocess

from privacy_scanner.scanner import PrivacyScanner
from privacy_scanner.utils.risk import RiskLevel
from privacy_scanner.device import Device

@pytest.fixture
def mock_device_info():
    return {
        'manufacturer': 'Test Manufacturer',
        'model': 'Test Model',
        'brand': 'Test Brand',
        'device': 'test_device',
        'android_version': '12',
        'security_patch': '2023-12',
        'identifiers': {
            'imei': ['123456789012345'],
            'imsi': ['310150123456789'],
            'phone_numbers': ['+1234567890'],
            'android_id': 'test_android_id',
            'ad_id': 'test_ad_id',
            'serial': 'test_serial',
            'mac_wifi': '00:11:22:33:44:55',
            'mac_bluetooth': 'AA:BB:CC:DD:EE:FF',
            'ip_addresses': ['192.168.1.100']
        }
    }

@pytest.fixture
def mock_app_details():
    return {
        'package_id': 'com.test.app',
        'app_name': 'Test App',
        'permissions': {
            'requested': ['android.permission.INTERNET'],
            'granted': ['android.permission.INTERNET'],
            'denied': []
        },
        'install_source': 'Google Play',
        'first_install_time': '2023-01-01',
        'last_update_time': '2023-12-01',
        'network_permissions': ['android.permission.INTERNET'],
        'shared_libraries': [],
        'shared_user_ids': []
    }

@pytest.fixture(autouse=True)
def mock_android_device(mock_device_info, mock_app_details):
    with patch('privacy_scanner.device.AndroidDevice') as MockAndroidDevice:
        device = MockAndroidDevice.return_value
        device.check_adb.return_value = True
        device.get_device_info.return_value = mock_device_info
        device.get_installed_apps.return_value = ['com.test.app']
        device.get_app_details.return_value = mock_app_details
        yield device

@pytest.fixture
def mock_device(mock_device_info, mock_app_details, mock_android_device):
    with patch('privacy_scanner.device.Device') as MockDevice:
        device = MockDevice.return_value
        device._device_info = mock_device_info
        device.get_device_info.return_value = mock_device_info
        device.get_installed_apps.return_value = ['com.test.app']
        device.get_app_details.return_value = mock_app_details
        device.device = mock_android_device
        return device

@pytest.fixture
def test_scanner(tmp_path):
    db_path = tmp_path / 'test_collectors.csv'
    with open(db_path, 'w') as f:
        f.write('app_name,package_id,collection_frequency,data_types\n')
        f.write('Test App,com.test.app,75,location\n')
    
    scanner = PrivacyScanner(db_path)
    return scanner

def test_device_info_collection(test_scanner, mock_device_info):
    """Test device information collection"""
    test_scanner.connect_device()
    assert test_scanner.device_info == mock_device_info
    assert 'manufacturer' in test_scanner.device_info
    assert 'identifiers' in test_scanner.device_info
    assert all(k in test_scanner.device_info['identifiers'] for k in ['imei', 'android_id', 'mac_wifi'])

def test_app_scanning(test_scanner, mock_app_details):
    """Test app scanning functionality"""
    test_scanner.connect_device()
    results = test_scanner.scan_apps()
    assert len(results) > 0
    assert 'com.test.app' in results
    app_result = results['com.test.app']
    assert app_result['app_name'] == 'Test App'
    assert app_result['risk_level'] == 'MEDIUM'  # Compare with string value

def test_report_generation(test_scanner, tmp_path):
    """Test report generation"""
    test_scanner.connect_device()
    scan_results = test_scanner.scan_apps()
    json_path, html_path = test_scanner.generate_report({
        'device_info': test_scanner.device_info,
        'apps': [scan_results['com.test.app']],  # Convert to list of apps
        'timestamp': '2024-01-09 15:47:59'
    }, tmp_path)
    
    # Check HTML report
    assert html_path.exists()
    
    # Check JSON data
    assert json_path.exists()
    with open(json_path) as f:
        data = json.load(f)
        assert 'device_info' in data
        assert 'apps' in data
        assert len(data['apps']) > 0

def test_error_handling(test_scanner):
    """Test error handling"""
    test_scanner.connect_device()
    with patch.object(test_scanner.device, 'get_installed_apps', side_effect=RuntimeError("Test error")):
        with pytest.raises(RuntimeError):
            test_scanner.scan_apps()
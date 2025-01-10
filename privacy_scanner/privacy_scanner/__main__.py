import argparse
from pathlib import Path
import sys
import os

from .scanner import PrivacyScanner
from .utils.risk import RiskLevel
from .utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description='Scan Android apps for privacy concerns using the Gravy Analytics dataset'
    )
    parser.add_argument(
        '--database',
        type=Path,
        default=Path('privacy_scanner/data/collectors_database.csv'),
        help='Path to the Gravy Analytics database CSV file'
    )
    parser.add_argument(
        '--reports-dir',
        type=str,
        default='privacy_scanner/reports',
        help='Base directory for reports (timestamped subdirectories will be created)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize scanner
        scanner = PrivacyScanner(args.database)
        
        # Perform scan
        scan_data = scanner.scan_device()
        
        # Generate reports
        json_path, html_path = scanner.generate_report(scan_data, args.reports_dir)
        
        # Print summary
        device_info = scan_data['device_info']
        identifiers = device_info.get('identifiers', {})
        
        print("\n📱 Device Information:")
        print(f"Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
        print(f"Model: {device_info.get('model', 'Unknown')}")
        print(f"Brand: {device_info.get('brand', 'Unknown')}")
        print(f"Android Version: {device_info.get('android_version', 'Unknown')}")
        print(f"Security Patch: {device_info.get('security_patch', 'Unknown')}")
        
        print("\n🔑 Device Identifiers:")
        print("System Identifiers:")
        print(f"  Serial Number: {identifiers.get('serial', 'Not available')}")
        print(f"  Android ID: {identifiers.get('android_id', 'Not available')}")
        
        print("\nNetwork Identifiers:")
        print(f"  IP Addresses: {', '.join(identifiers.get('ip_addresses', [])) or 'Not available'}")
        print(f"  Bluetooth MAC: {identifiers.get('mac_bluetooth', 'Not available')}")
        
        high_risk = len([a for a in scan_data['apps'] if a['risk_level'] == RiskLevel.HIGH])
        medium_risk = len([a for a in scan_data['apps'] if a['risk_level'] == RiskLevel.MEDIUM])
        low_risk = len([a for a in scan_data['apps'] if a['risk_level'] == RiskLevel.LOW])
        unknown = len([a for a in scan_data['apps'] if a['risk_level'] == RiskLevel.NOT_FOUND])
        
        print("\n📱 App Summary:")
        print(f"Total installed apps: {scan_data['total_apps']}")
        print(f"High risk apps: {high_risk}")
        print(f"Medium risk apps: {medium_risk}")
        print(f"Low risk apps: {low_risk}")
        print(f"Unknown apps: {unknown}")
        
        print(f"\n📄 Reports generated in: {os.path.dirname(html_path)}")
        print(f"- HTML Report: {html_path}")
        print(f"- Full JSON Data: {json_path}")
        
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
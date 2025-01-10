"""Scanner module for privacy analysis"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .device import Device
from .database import CollectorsDatabase
from .report import generate_html_report
from .utils.logger import setup_logger
from .utils.risk import RiskLevel, categorize_permissions

logger = setup_logger(__name__)

class PrivacyScanner:
    """Privacy scanner for Android apps"""
    
    def __init__(self, database_path: Path = Path('privacy_scanner/data/collectors_database.csv')):
        """Initialize scanner with database path"""
        self.database = CollectorsDatabase(database_path)
        self.device = None
        self.scan_results = {}
        self.device_info = {}
        
    def connect_device(self):
        """Connect to Android device"""
        try:
            self.device = Device()
            self.device_info = self.device.get_device_info()
            logger.info("Successfully connected to device")
        except Exception as e:
            logger.error(f"Failed to connect to device: {str(e)}")
            raise
    
    def scan_apps(self) -> Dict:
        """Scan installed apps and check against database"""
        if not self.device:
            raise RuntimeError("No device connected. Call connect_device() first")
            
        results = {}
        try:
            installed_apps = self.device.get_installed_apps()
            logger.info(f"Starting scan of {len(installed_apps)} installed apps...")
            
            for i, package_id in enumerate(installed_apps, 1):
                try:
                    if i % 10 == 0:  # Log progress every 10 apps
                        logger.info(f"Progress: {i}/{len(installed_apps)} apps scanned")
                    
                    logger.debug(f"Getting details for app: {package_id}")
                    app_details = self.device.get_app_details(package_id)
                    logger.debug(f"Got app details: {app_details}")
                    
                    logger.debug(f"Looking up app in database: {package_id}")
                    app_data = self.database.get_app_details(package_id)
                    logger.debug(f"Database lookup result: {app_data}")
                    
                    risk_level = self.database.get_risk_level(package_id)
                    logger.debug(f"Risk level determined: {risk_level}")
                    
                    results[package_id] = {
                        'app_name': app_details['app_name'],
                        'package_id': package_id,
                        'permissions': app_details['permissions'],
                        'install_source': app_details['install_source'],
                        'first_install_time': app_details['first_install_time'],
                        'last_update_time': app_details['last_update_time'],
                        'risk_level': risk_level.name,
                        'collection_frequency': app_data.get('collection_frequency', 0) if app_data else 0,
                        'data_types': app_data.get('data_types', []) if app_data else []
                    }
                    
                    # Only log high-risk apps or errors
                    if risk_level.name == 'HIGH':
                        logger.warning(f"High-risk app found: {app_details['app_name']} ({package_id})")
                    
                except Exception as e:
                    logger.error(f"Error scanning {package_id}: {str(e)}")
                    logger.exception("Full traceback:")
                    continue
                    
            logger.info(f"Scan completed. Processed {len(results)} apps successfully.")
            self.scan_results = results
            return results
            
        except Exception as e:
            logger.error(f"Fatal error during app scanning: {str(e)}")
            logger.exception("Full traceback:")
            raise
    
    def scan_device(self) -> Dict:
        """Run full device scan and return results"""
        self.connect_device()
        apps = self.scan_apps()
        return {
            'device_info': self.device_info,
            'apps': list(apps.values()),
            'total_apps': len(apps),
            'timestamp': datetime.now().isoformat()
        }

    def generate_report(self, scan_data: Dict, output_dir: Optional[str] = None) -> tuple[Path, Path]:
        """Generate HTML and JSON reports with improved organization"""
        # Create timestamped directory with device info
        timestamp = datetime.now().strftime('%Y-%m-%d')
        device_info = scan_data['device_info']
        device_name = f"{device_info.get('manufacturer', 'unknown')}_{device_info.get('model', 'device')}_{device_info['identifiers'].get('android_id', '')[-5:]}"
        output_dir = Path('privacy_scanner/reports') / f"{timestamp}_{device_name}"
        
        logger.info(f"Creating report directory: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhance the JSON structure
        enhanced_data = {
            "scan_info": {
                "timestamp": datetime.now().isoformat(),
                "scanner_version": "1.0.0"
            },
            "device_info": scan_data['device_info'],
            "summary": {
                "total_apps": len(scan_data['apps']),
                "risk_levels": {
                    "high": len([a for a in scan_data['apps'] if a['risk_level'] == 'HIGH']),
                    "medium": len([a for a in scan_data['apps'] if a['risk_level'] == 'MEDIUM']),
                    "low": len([a for a in scan_data['apps'] if a['risk_level'] == 'LOW']),
                    "unknown": len([a for a in scan_data['apps'] if a['risk_level'] == 'NOT_FOUND'])
                },
                "permissions_summary": {
                    "total_permissions_requested": sum(len(a['permissions']['requested']) for a in scan_data['apps']),
                    "total_permissions_granted": sum(len(a['permissions']['granted']) for a in scan_data['apps']),
                    "total_permissions_denied": sum(len(a['permissions']['denied']) for a in scan_data['apps'])
                }
            },
            "apps": []
        }

        # Enhance each app's data
        for app in scan_data['apps']:
            permissions = app['permissions']
            categorized_permissions = categorize_permissions(permissions['requested'])
            
            enhanced_app = {
                "app_info": {
                    "name": app['app_name'],
                    "package_id": app['package_id'],
                    "install_source": app['install_source'],
                    "first_install_time": app['first_install_time'],
                    "last_update_time": app['last_update_time']
                },
                "risk_assessment": {
                    "level": app['risk_level'],
                    "score": self.database.get_risk_score(app['package_id']),
                    "factors": self.database.get_risk_factors(app['package_id'])
                },
                "permissions": {
                    "summary": {
                        "total_requested": len(permissions['requested']),
                        "total_granted": len(permissions['granted']),
                        "total_denied": len(permissions['denied'])
                    },
                    "categorized": categorized_permissions,
                    "details": {
                        "granted": permissions['granted'],
                        "denied": permissions['denied']
                    }
                },
                "data_collection": {
                    "frequency": app['collection_frequency'],
                    "types": app['data_types'],
                    "known_behaviors": self.database.get_known_behaviors(app['package_id'])
                }
            }
            enhanced_data['apps'].append(enhanced_app)

        # Save enhanced JSON
        base_filename = f"report_{device_name}"
        json_path = output_dir / f"{base_filename}.json"
        logger.info(f"Writing enhanced JSON report to: {json_path}")
        with open(json_path, 'w') as f:
            json.dump(enhanced_data, f, indent=2)
            
        # Generate HTML report
        html_path = output_dir / f"{base_filename}.html"
        logger.info(f"Writing HTML report to: {html_path}")
        generate_html_report(scan_data['device_info'], {app['package_id']: app for app in scan_data['apps']}, html_path)
        
        logger.info(f"Reports generated in {output_dir}")
        return json_path, html_path
"""Report generation module"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json

from .utils.logger import setup_logger
from .utils.risk import RiskLevel

logger = setup_logger(__name__)

def generate_html_report(device_info: Dict, scan_results: Dict, output_path: Path) -> None:
    """Generate HTML report from scan results"""
    logger.info(f"Generating HTML report at {output_path}")
    
    # Count apps by risk level
    risk_counts = {
        RiskLevel.HIGH: 0,
        RiskLevel.MEDIUM: 0,
        RiskLevel.LOW: 0,
        RiskLevel.NOT_FOUND: 0
    }
    
    logger.info(f"Processing {len(scan_results)} apps")
    for app in scan_results.values():
        risk_level = RiskLevel[app['risk_level']]
        risk_counts[risk_level] += 1
    
    logger.info(f"Risk level counts: {risk_counts}")
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy Scanner Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1, h2 {{ color: #333; }}
            .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .risk-high {{ color: #d32f2f; }}
            .risk-medium {{ color: #f57c00; }}
            .risk-low {{ color: #388e3c; }}
            .risk-unknown {{ color: #757575; }}
            .identifier {{ margin: 10px 0; }}
            .app-list {{ margin-top: 10px; }}
            .app-item {{ padding: 10px; border-bottom: 1px solid #eee; }}
        </style>
    </head>
    <body>
        <h1>Privacy Scanner Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="section">
            <h2>Device Information</h2>
            <p>Manufacturer: {device_info.get('manufacturer', 'Unknown')}</p>
            <p>Model: {device_info.get('model', 'Unknown')}</p>
            <p>Android Version: {device_info.get('android_version', 'Unknown')}</p>
            <p>Security Patch: {device_info.get('security_patch', 'Unknown')}</p>
            
            <h3>Device Identifiers</h3>
            <div class="identifier">
                <strong>Android ID:</strong> {device_info['identifiers'].get('android_id', 'Not available')}
                <br><small>Resets on factory reset</small>
            </div>
            <div class="identifier">
                <strong>Bluetooth MAC:</strong> {device_info['identifiers'].get('mac_bluetooth', 'Not available')}
            </div>
            <div class="identifier">
                <strong>IP Addresses:</strong> {', '.join(device_info['identifiers'].get('ip_addresses', ['Not available']))}
            </div>
        </div>
        
        <div class="section">
            <h2>Scan Summary</h2>
            <p>Total Apps Scanned: {len(scan_results)}</p>
            <p class="risk-high">High Risk Apps: {risk_counts[RiskLevel.HIGH]}</p>
            <p class="risk-medium">Medium Risk Apps: {risk_counts[RiskLevel.MEDIUM]}</p>
            <p class="risk-low">Low Risk Apps: {risk_counts[RiskLevel.LOW]}</p>
            <p class="risk-unknown">Not Found in Database: {risk_counts[RiskLevel.NOT_FOUND]}</p>
        </div>
        
        <div class="section">
            <h2>High Risk Apps</h2>
            <div class="app-list">
                {_generate_app_list(scan_results, RiskLevel.HIGH)}
            </div>
        </div>
        
        <div class="section">
            <h2>Medium Risk Apps</h2>
            <div class="app-list">
                {_generate_app_list(scan_results, RiskLevel.MEDIUM)}
            </div>
        </div>
        
        <div class="section">
            <h2>Low Risk Apps</h2>
            <div class="app-list">
                {_generate_app_list(scan_results, RiskLevel.LOW)}
            </div>
        </div>
        
        <div class="section">
            <h2>Apps Not Found in Database</h2>
            <div class="app-list">
                {_generate_app_list(scan_results, RiskLevel.NOT_FOUND)}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Create parent directory if it doesn't exist
    logger.info(f"Creating parent directory: {output_path.parent}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write HTML content to file
    logger.info(f"Writing HTML content to file: {output_path}")
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"HTML report generated at {output_path}")

def _generate_app_list(scan_results: Dict, risk_level: RiskLevel) -> str:
    """Generate HTML list of apps for a given risk level"""
    app_list = []
    for app in scan_results.values():
        if RiskLevel[app['risk_level']] == risk_level:
            app_list.append(f"""
                <div class="app-item">
                    <strong>{app['app_name']}</strong> ({app['package_id']})
                    <br>Collection Frequency: {app['collection_frequency']}
                    <br>Data Types: {', '.join(app['data_types']) if app['data_types'] else 'None'}
                    <br>Permissions: {', '.join(app['permissions']) if app['permissions'] else 'None'}
                    <br>Install Source: {app['install_source']}
                    <br>First Install: {app['first_install_time']}
                    <br>Last Update: {app['last_update_time']}
                </div>
            """)
    return '\n'.join(app_list) if app_list else '<p>No apps found in this category</p>'

# Privacy Scanner

[![CI](https://github.com/yourusername/privacy-scanner/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/privacy-scanner/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A privacy analysis tool for Android applications that scans installed apps and cross-references them with the Gravy Analytics dataset to assess privacy risks.

## Features

- Scans installed Android apps and cross-references with Gravy Analytics dataset
- Collects comprehensive device information including:
  - Hardware identifiers (Serial, Android ID)
  - Network identifiers (IP addresses, Bluetooth MAC)
  - System information (Android version, security patch)
- Generates detailed privacy reports in both HTML and JSON formats
- Analyzes app permissions and data access
- Current risk scoring system:
  - Base score from data collection frequency
  - Multiplier based on number of data types collected (10% per type)
  - Risk levels:
    - High Risk (Score > 75): Very frequent data collection
    - Medium Risk (Score > 25): Moderate data collection
    - Low Risk (Score ≤ 25): Minimal data collection
    - Not Found: Apps not present in the database
- Shows detailed app information including:
  - Application name and package ID
  - Installation source
  - First install and last update times
  - Granted and denied permissions
  - Permission categories (location, camera, contacts, etc.)
- Robust error handling and logging
- Clear warning messages for database issues

## Planned Improvements

- Enhanced risk scoring system considering:
  - Privacy-critical permissions weight
  - Known malicious behavior patterns
  - App source verification
  - Historical privacy violations
  - Data sharing practices
- Additional device identifiers collection
- More detailed permission analysis
- Network traffic analysis
- Shared library scanning
- Custom database support

## Requirements

- Python 3.8+
- Android Debug Bridge (ADB) installed and in PATH
- Android device with USB debugging enabled
- Required Python packages (install via requirements.txt):
  ```
  pandas>=1.5.0
  pytest>=7.0.0
  black>=22.0.0
  mypy>=1.0.0
  setuptools>=75.0.0
  typing-extensions>=4.0.0
  python-dateutil>=2.8.0
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/privacy-scanner.git
   cd privacy-scanner
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

1. Connect your Android device via USB and enable USB debugging

2. Verify ADB connection:
   ```bash
   adb devices
   ```

3. Run the scanner:
   ```bash
   python -m privacy_scanner
   ```

4. The scanning process will:
   - Load the Gravy Analytics database
   - Connect to your Android device
   - Collect device information
   - Scan all installed applications
   - Generate detailed HTML and JSON reports

5. View the reports in the `privacy_scanner/reports` directory:
   - HTML report: `privacy_scanner/reports/YYYY-MM-DD_manufacturer_model_androidid/report_*.html`
   - Full JSON data: `privacy_scanner/reports/YYYY-MM-DD_manufacturer_model_androidid/report_*.json`

## Report Format

The scanner generates two types of reports:

1. **HTML Report**:
   - Device information section
   - Risk-level summary with counts
   - Categorized app listings by risk level
   - Detailed app information including permissions
   - Permission categorization (privacy-critical, by type)

2. **JSON Report**:
   ```json
   {
     "scan_info": {
       "timestamp": "2024-01-09T20:08:26",
       "scanner_version": "1.0.0"
     },
     "device_info": {
       "manufacturer": "Google",
       "model": "Pixel 9 Pro",
       "android_version": "15",
       "identifiers": { ... }
     },
     "summary": {
       "total_apps": 417,
       "risk_levels": {
         "high": 12,
         "medium": 45,
         "low": 320,
         "unknown": 40
       },
       "permissions_summary": { ... }
     },
     "apps": [
       {
         "app_info": {
           "name": "App Name",
           "package_id": "com.example.app",
           "install_source": "Google Play",
           "first_install_time": "2024-01-01"
         },
         "risk_assessment": {
           "level": "HIGH",
           "score": 85.5,
           "factors": ["High data collection frequency", ...]
         },
         "permissions": {
           "summary": { ... },
           "categorized": {
             "privacy_critical": [...],
             "categories": {
               "location": [...],
               "camera": [...],
               "storage": [...]
             }
           }
         },
         "data_collection": {
           "frequency": 75,
           "types": ["location", "contacts"],
           "known_behaviors": [...]
         }
       }
     ]
   }
   ```

## Testing

Run the test suite:
```bash
pytest -v privacy_scanner/tests/
```

## Security Considerations

- The tool only reads data from your device and does not modify any settings
- All scan results are stored locally
- No data is sent to external servers
- Permission analysis is read-only
- Some identifiers may not be accessible due to Android security restrictions
- Clear warning messages for database issues 

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/privacy-scanner.git
   cd privacy-scanner
   ```
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your feature"
   git push origin feature/your-feature-name
   ```
6. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Gravy Analytics for providing the data collection dataset
- The Android Debug Bridge (ADB) team
- All contributors to this project 
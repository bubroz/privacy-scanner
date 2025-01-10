# Privacy Scanner

A Python-based tool that helps users identify which of their installed Android applications are potentially selling their data, based on the Gravy Analytics leaked dataset (https://github.com/bubroz/privacy-scanner/blob/main/privacy_scanner/data/collectors_database.csv). The tool provides risk assessments and detailed reports about data collection practices.

## Features

- Scans installed Android apps and cross-references with Gravy Analytics dataset
- Collects comprehensive device information including:
  - Hardware identifiers (Bluetooth MAC address)
  - Network identifiers (IP addresses, Android ID)
- Generates detailed privacy reports in both HTML and JSON formats
- Analyzes app permissions and data access
- Provides risk scoring based on data collection frequency
- Shows detailed app information including:
  - Application name and package ID
  - Installation source
  - First install and last update times
  - Granted and denied permissions
  - Network access capabilities
  - Shared libraries and user IDs
- Robust error handling and fallback mechanisms
- Clear warning messages for inaccessible identifiers

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
   cd privacy_scanner
   python -m privacy_scanner.__main__
   ```

4. The scanning process will:
   - Load the Gravy Analytics database
   - Connect to your Android device
   - Collect device information and identifiers
   - Scan all installed applications
   - Generate detailed HTML and JSON reports

5. View the reports in the `reports` directory:
   - HTML report: `reports/<timestamp>_<device>/privacy_report.html`
   - Full JSON data: `reports/<timestamp>_<device>/scan_data.json`

## Understanding the Scanning Process

The scanner operates in several phases:

1. **Database Loading**
   - Loads the Gravy Analytics dataset
   - Processes and cleans app names and identifiers
   - Prepares risk scoring system
   - Handles malformed data gracefully

2. **Device Information Collection**
   - Basic device info (manufacturer, model, Android version)
   - Hardware identifiers (may require permissions)
   - Network and subscriber information
   - Current device state and security patch level
   - Fallback mechanisms for alternate interface names
   - Validation of identifier formats

3. **App Analysis** (for each installed app)
   - Extracts app name and package information
   - Analyzes permissions (requested, granted, denied)
   - Checks installation source and timestamps
   - Identifies network capabilities
   - Cross-references with Gravy Analytics data
   - Handles various app label formats

4. **Risk Assessment**
   - **High Risk** (Score ≥ 150): Apps with very frequent data collection
   - **Medium Risk** (Score ≥ 50): Moderate data collection
   - **Low Risk** (Score < 50): Minimal data collection
   - **Not Found**: Apps not present in the database

5. **Report Generation**
   - Creates timestamped report directory
   - Generates detailed HTML report with:
     - Device information section
     - Identifier explanations and availability status
     - Risk-categorized app listings
     - Clear indicators for unavailable data
   - Saves complete JSON data for further analysis

## Testing

The project includes comprehensive test suites to ensure reliability:

1. **Database Tests** (`tests/test_database.py`):
   - Database loading and validation
   - Risk level calculation
   - Malformed data handling
   - App name cleaning and normalization

2. **Scanner Tests** (`tests/test_scanner.py`):
   - Device information collection
   - App scanning functionality
   - Report generation
   - Error handling and fallbacks

To run the tests:
```bash
pytest privacy_scanner/tests/
```

For verbose output:
```bash
pytest -v privacy_scanner/tests/
```

For test coverage:
```bash
pytest --cov=privacy_scanner privacy_scanner/tests/
```

## Security Considerations

- The tool only reads data from your device and does not modify any settings
- All scan results are stored locally
- No data is sent to external servers
- Permission analysis is read-only
- Some identifiers may not be accessible due to Android security restrictions:
  - IMEI/IMSI require READ_PHONE_STATE permission
  - MAC addresses may be restricted on newer Android versions
  - Some identifiers may require root access
- Clear warning messages when permissions are needed
- Validation of identifier formats before reporting

## Future Enhancements

1. GUI Interface
2. Real-time scanning
3. Custom risk assessment rules
4. Export to different formats
5. Batch processing
6. Network traffic analysis
7. Historical tracking
8. Alternative data sources
9. Permission request handling
10. Root capability support
11. Enhanced error reporting
12. Custom database support

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Write or update tests:
   - Add tests for new functionality
   - Ensure existing tests pass
   - Follow test naming conventions
   - Include docstrings for test functions
5. Run the test suite:
   ```bash
   pytest privacy_scanner/tests/
   ```
6. Push to the branch
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. It helps users understand which apps may be collecting and selling their data based on the Gravy Analytics dataset. The risk levels and assessments are based on data collection frequency and should not be considered definitive proof of malicious behavior. Some device identifiers may not be accessible due to Android security restrictions. The tool provides clear warnings when it cannot access certain information due to permissions or system restrictions. 

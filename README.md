# Privacy Scanner

A Python-based tool that helps users identify which of their installed Android applications are potentially selling their data, based on the Gravy Analytics leaked dataset. The tool scans installed apps and provides risk assessments based on data collection frequency.

## Features

- Scans installed Android apps and cross-references with Gravy Analytics dataset
- Collects device information including:
  - Network identifiers (IP addresses)
  - Android ID
  - Bluetooth MAC address
  - Serial number
- Generates detailed privacy reports in both HTML and JSON formats
- Analyzes app permissions and installation details
- Provides risk scoring based on data collection frequency:
  - High Risk (> 75 occurrences)
  - Medium Risk (26-75 occurrences)
  - Low Risk (1-25 occurrences)
  - Not Found (app not in database)

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
   git clone https://github.com/bubroz/privacy-scanner.git
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

5. View the reports in the `reports` directory:
   - HTML report: `reports/<timestamp>_<device>/report_<device>.html`
   - Full JSON data: `reports/<timestamp>_<device>/report_<device>.json`

## Understanding the Reports

The scanner generates two types of reports:

1. **HTML Report**
   - Device information section
   - Summary of risk levels across all apps
   - Detailed app listings with:
     - Installation details
     - Permission information
     - Risk assessment
     - Known behaviors

2. **JSON Report**
   - Complete scan data including:
     - Device information
     - Risk level statistics
     - Detailed app data
     - Permission summaries
     - Risk assessments

## Risk Assessment

Apps are categorized based on their data collection frequency:
- **High Risk** (> 75 occurrences): Very frequent data collection
- **Medium Risk** (26-75 occurrences): Moderate data collection
- **Low Risk** (1-25 occurrences): Minimal data collection
- **Not Found**: Apps not present in the database

## Testing

The project includes test suites for database and scanner functionality:

```bash
# Run all tests
pytest privacy_scanner/tests/

# Run with verbose output
pytest -v privacy_scanner/tests/

# Run with coverage report
pytest --cov=privacy_scanner privacy_scanner/tests/
```

## Security Considerations

- The tool only reads data from your device and does not modify any settings
- All scan results are stored locally
- No data is sent to external servers
- Permission analysis is read-only
- Some identifiers may not be accessible due to Android security restrictions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Write or update tests
5. Run the test suite
6. Push to the branch
7. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. It helps users understand which apps may be collecting their data based on the Gravy Analytics dataset. The risk levels are based solely on data collection frequency and should not be considered definitive proof of malicious behavior.

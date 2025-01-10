import pytest
from pathlib import Path
import pandas as pd
from privacy_scanner.database import CollectorsDatabase
from privacy_scanner.utils.risk import RiskLevel

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'app_name': ['Test App 1', 'Test App 2', 'Test App 3'],
        'package_id': ['com.test.app1', 'com.test.app2', 'com.test.app3'],
        'collection_frequency': [200, 75, 25],
        'data_types': ['location,contacts', 'location', 'device_info']
    })

@pytest.fixture
def test_db(tmp_path, sample_data):
    csv_path = tmp_path / 'test_collectors.csv'
    sample_data.to_csv(csv_path, index=False)
    return CollectorsDatabase(csv_path)

def test_database_loading(test_db):
    """Test that database loads correctly"""
    assert len(test_db.data) == 3
    assert 'app_name' in test_db.data.columns
    assert 'package_id' in test_db.data.columns
    assert 'collection_frequency' in test_db.data.columns

def test_risk_level_calculation(test_db):
    """Test risk level calculation for different scores"""
    # High risk app
    assert test_db.get_risk_level('com.test.app1') == RiskLevel.HIGH
    # Medium risk app
    assert test_db.get_risk_level('com.test.app2') == RiskLevel.MEDIUM
    # Low risk app
    assert test_db.get_risk_level('com.test.app3') == RiskLevel.LOW
    # Not found app
    assert test_db.get_risk_level('com.test.nonexistent') == RiskLevel.NOT_FOUND

def test_malformed_data_handling(tmp_path):
    """Test handling of malformed data in CSV"""
    malformed_data = pd.DataFrame({
        'app_name': ['Bad App', None, 'Test App'],
        'package_id': ['com.bad.app', 'com.null.app', 'com.test.app'],
        'collection_frequency': ['invalid', 50, 25],
        'data_types': [None, 'location', 'device_info']
    })
    
    csv_path = tmp_path / 'malformed_collectors.csv'
    malformed_data.to_csv(csv_path, index=False)
    
    # Should not raise any exceptions
    db = CollectorsDatabase(csv_path)
    assert len(db.data) > 0  # Some data should be loaded
    
    # Test risk level for malformed entry
    assert db.get_risk_level('com.bad.app') == RiskLevel.LOW  # Default to low risk

def test_app_name_cleaning(test_db):
    """Test app name cleaning and normalization"""
    # Get app details should work with different package ID formats
    details = test_db.get_app_details('com.test.app1')
    assert details is not None
    assert 'app_name' in details
    assert 'collection_frequency' in details
    
    # Should handle case differences
    details = test_db.get_app_details('COM.TEST.APP1')
    assert details is not None 
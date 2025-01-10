"""Database module for privacy analysis"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from .utils.risk import RiskLevel
from .utils.logger import setup_logger

logger = setup_logger(__name__)

class CollectorsDatabase:
    """Database of known data collectors and their behaviors"""
    
    def __init__(self, database_path: Path):
        """Initialize database from CSV file"""
        try:
            self.df = pd.read_csv(database_path)
            logger.info(f"Available columns: {list(self.df.columns)}")
            logger.info(f"Database loaded with {len(self.df)} apps")
        except Exception as e:
            logger.error(f"Failed to load database: {str(e)}")
            raise

    def get_app_details(self, package_id: str) -> Optional[Dict]:
        """Get details for an app from the database"""
        try:
            app_data = self.df[self.df['APK'] == package_id]
            if len(app_data) == 0:
                return None
                
            row = app_data.iloc[0]
            return {
                'collection_frequency': self._parse_frequency(row.get('collection_frequency', 0)),
                'data_types': self._parse_data_types(row.get('data_types', ''))
            }
        except Exception as e:
            logger.warning(f"Error getting app details for {package_id}: {str(e)}")
            return None

    def get_risk_level(self, package_id: str) -> RiskLevel:
        """Get risk level for an app"""
        try:
            app_data = self.df[self.df['APK'] == package_id]
            if len(app_data) == 0:
                return RiskLevel.NOT_FOUND
                
            row = app_data.iloc[0]
            frequency = self._parse_frequency(row.get('collection_frequency', 0))
            
            if frequency > 75:
                return RiskLevel.HIGH
            elif frequency > 25:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW
                
        except Exception as e:
            logger.warning(f"Error getting risk level for {package_id}: {str(e)}")
            return RiskLevel.NOT_FOUND

    def get_risk_score(self, package_id: str) -> float:
        """Get numerical risk score (0-100) for an app"""
        try:
            app_data = self.df[self.df['APK'] == package_id]
            if len(app_data) == 0:
                return 0.0
                
            row = app_data.iloc[0]
            base_score = self._parse_frequency(row.get('collection_frequency', 0))
            
            # Adjust score based on data types collected
            data_types = self._parse_data_types(row.get('data_types', ''))
            sensitive_multiplier = 1.0 + (len(data_types) * 0.1)  # 10% increase per data type
            
            return min(100.0, base_score * sensitive_multiplier)
            
        except Exception as e:
            logger.warning(f"Error calculating risk score for {package_id}: {str(e)}")
            return 0.0

    def get_risk_factors(self, package_id: str) -> List[str]:
        """Get list of risk factors for an app"""
        try:
            app_data = self.df[self.df['APK'] == package_id]
            if len(app_data) == 0:
                return []
                
            factors = []
            row = app_data.iloc[0]
            
            # Check collection frequency
            frequency = self._parse_frequency(row.get('collection_frequency', 0))
            if frequency > 75:
                factors.append("High data collection frequency")
            elif frequency > 25:
                factors.append("Moderate data collection frequency")
                
            # Check data types
            data_types = self._parse_data_types(row.get('data_types', ''))
            if 'location' in data_types:
                factors.append("Collects location data")
            if 'contacts' in data_types:
                factors.append("Accesses contact information")
            if 'camera' in data_types:
                factors.append("Uses camera")
            if 'microphone' in data_types:
                factors.append("Uses microphone")
                
            return factors
            
        except Exception as e:
            logger.warning(f"Error getting risk factors for {package_id}: {str(e)}")
            return []

    def get_known_behaviors(self, package_id: str) -> List[str]:
        """Get list of known behaviors for an app"""
        try:
            app_data = self.df[self.df['APK'] == package_id]
            if len(app_data) == 0:
                return []
                
            behaviors = []
            row = app_data.iloc[0]
            
            # Add known behaviors based on data types and frequency
            data_types = self._parse_data_types(row.get('data_types', ''))
            frequency = self._parse_frequency(row.get('collection_frequency', 0))
            
            if frequency > 0:
                behaviors.append(f"Collects data approximately {frequency} times per day")
            
            for data_type in data_types:
                behaviors.append(f"Known to collect {data_type} data")
                
            return behaviors
            
        except Exception as e:
            logger.warning(f"Error getting known behaviors for {package_id}: {str(e)}")
            return []

    def _parse_frequency(self, value: any) -> int:
        """Parse collection frequency value, with error handling"""
        try:
            if pd.isna(value) or value == '':
                return 0
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                # Try to extract numeric value
                import re
                numbers = re.findall(r'\d+', value)
                if numbers:
                    return int(numbers[0])
            logger.warning(f"Invalid collection frequency value: {value}, defaulting to 0")
            return 0
        except Exception as e:
            logger.warning(f"Error parsing frequency value {value}: {str(e)}")
            return 0

    def _parse_data_types(self, value: str) -> List[str]:
        """Parse data types string into list"""
        try:
            if pd.isna(value) or value == '':
                return []
            if isinstance(value, str):
                return [t.strip().lower() for t in value.split(',')]
            return []
        except Exception as e:
            logger.warning(f"Error parsing data types {value}: {str(e)}")
            return []

"""Risk assessment utilities"""

from enum import Enum
from typing import Dict, List, Set

class RiskLevel(Enum):
    """Risk levels for apps"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    NOT_FOUND = "NOT_FOUND"

# Define permission categories and their members
PERMISSION_CATEGORIES = {
    "location": {
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",
        "android.permission.ACCESS_BACKGROUND_LOCATION"
    },
    "camera": {
        "android.permission.CAMERA"
    },
    "microphone": {
        "android.permission.RECORD_AUDIO"
    },
    "contacts": {
        "android.permission.READ_CONTACTS",
        "android.permission.WRITE_CONTACTS",
        "android.permission.GET_ACCOUNTS"
    },
    "storage": {
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",
        "android.permission.MANAGE_EXTERNAL_STORAGE",
        "android.permission.ACCESS_MEDIA_LOCATION"
    },
    "phone": {
        "android.permission.READ_PHONE_STATE",
        "android.permission.CALL_PHONE",
        "android.permission.READ_CALL_LOG",
        "android.permission.WRITE_CALL_LOG",
        "android.permission.ADD_VOICEMAIL",
        "android.permission.USE_SIP",
        "android.permission.PROCESS_OUTGOING_CALLS"
    },
    "sms": {
        "android.permission.SEND_SMS",
        "android.permission.RECEIVE_SMS",
        "android.permission.READ_SMS",
        "android.permission.RECEIVE_WAP_PUSH",
        "android.permission.RECEIVE_MMS"
    },
    "calendar": {
        "android.permission.READ_CALENDAR",
        "android.permission.WRITE_CALENDAR"
    },
    "sensors": {
        "android.permission.BODY_SENSORS",
        "android.permission.USE_FINGERPRINT",
        "android.permission.USE_BIOMETRIC"
    },
    "activity_recognition": {
        "android.permission.ACTIVITY_RECOGNITION"
    }
}

# Define privacy critical permissions
PRIVACY_CRITICAL_PERMISSIONS: Set[str] = set().union(*PERMISSION_CATEGORIES.values())

def categorize_permissions(permissions: List[str]) -> Dict[str, List[str]]:
    """Categorize permissions into meaningful groups"""
    result = {
        "privacy_critical": [],
        "categories": {category: [] for category in PERMISSION_CATEGORIES.keys()},
        "other": []
    }
    
    for permission in permissions:
        # Check if it's privacy critical
        if permission in PRIVACY_CRITICAL_PERMISSIONS:
            result["privacy_critical"].append(permission)
            
        # Categorize by type
        categorized = False
        for category, perms in PERMISSION_CATEGORIES.items():
            if permission in perms:
                result["categories"][category].append(permission)
                categorized = True
                break
                
        # If not in any category, add to other
        if not categorized:
            result["other"].append(permission)
    
    # Remove empty categories
    result["categories"] = {k: v for k, v in result["categories"].items() if v}
    
    return result 
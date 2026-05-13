"""
Firebase Configuration Module
==============================
Initializes Firebase Admin SDK and provides Firestore client.
Requires a serviceAccountKey.json file in the project root.

HOW TO GET THE SERVICE ACCOUNT KEY:
1. Go to https://console.firebase.google.com/
2. Select your project (campus-l-and-f)
3. Click ⚙️ Project Settings > Service Accounts
4. Click "Generate New Private Key"
5. Save the downloaded JSON file as 'serviceAccountKey.json'
   in the lost_found_system/ folder
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore

# Path to the service account key file
KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')

_db = None


def init_firebase():
    """
    Initialize Firebase Admin SDK and return Firestore client.
    Call this once at app startup.
    """
    global _db

    if not os.path.exists(KEY_PATH):
        print("\n" + "=" * 60)
        print("ERROR: serviceAccountKey.json NOT FOUND!")
        print("=" * 60)
        print("To get your Firebase service account key:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Select project 'campus-l-and-f'")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Click 'Generate New Private Key'")
        print(f"5. Save the file as: {KEY_PATH}")
        print("=" * 60 + "\n")
        raise FileNotFoundError("serviceAccountKey.json is required. See instructions above.")

    if not firebase_admin._apps:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)

    _db = firestore.client()
    return _db


def get_db():
    """Get the Firestore client instance."""
    global _db
    if _db is None:
        _db = init_firebase()
    return _db

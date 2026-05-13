"""
Firebase Configuration Module
==============================
Supports two modes:
1. Local: reads serviceAccountKey.json file
2. Deployed (Render): reads FIREBASE_CREDENTIALS environment variable
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

KEY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'serviceAccountKey.json')
_db = None


def init_firebase():
    global _db
    if firebase_admin._apps:
        _db = firestore.client()
        return _db

    # Option 1: Environment variable (for Render/hosting)
    env_creds = os.environ.get('FIREBASE_CREDENTIALS')
    if env_creds:
        cred_dict = json.loads(env_creds)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        return _db

    # Option 2: Local JSON file
    if os.path.exists(KEY_PATH):
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        return _db

    raise FileNotFoundError(
        "Firebase credentials not found!\n"
        "Either set FIREBASE_CREDENTIALS env var or place serviceAccountKey.json in project root."
    )


def get_db():
    global _db
    if _db is None:
        _db = init_firebase()
    return _db

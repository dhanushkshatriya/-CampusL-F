"""
Helper Utilities Module
=======================
General helper functions used across the application.
"""

import os
import uuid
from datetime import datetime

# Allowed image extensions for upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Item categories used across the application
CATEGORIES = [
    'Electronics', 'Books & Stationery', 'Clothing', 'Accessories',
    'ID Cards & Documents', 'Keys', 'Bags & Wallets', 'Water Bottles',
    'Sports Equipment', 'Jewelry', 'Umbrella', 'Other'
]

# Campus locations for dropdowns
LOCATIONS = [
    'Main Library', 'Science Building', 'Arts Block', 'Engineering Lab',
    'Student Center', 'Cafeteria', 'Auditorium', 'Sports Complex',
    'Computer Lab', 'Parking Lot', 'Main Gate', 'Admin Office',
    'Lecture Hall A', 'Lecture Hall B', 'Lecture Hall C',
    'Boys Hostel', 'Girls Hostel', 'Playground', 'Canteen', 'Other'
]

# Departments
DEPARTMENTS = [
    'Computer Science', 'Electronics', 'Mechanical', 'Civil',
    'Electrical', 'Information Technology', 'MBA', 'MCA',
    'Science', 'Arts', 'Commerce', 'Law', 'Staff', 'Other'
]


def allowed_file(filename):
    """Check if uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file, upload_folder):
    """
    Save an uploaded image file with a unique name.
    Returns the filename (not the full path).
    """
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filename
    return None


def format_date(date_str):
    """Format a date string for display."""
    if not date_str:
        return 'N/A'
    try:
        dt = datetime.strptime(str(date_str)[:10], '%Y-%m-%d')
        return dt.strftime('%d %b %Y')
    except (ValueError, TypeError):
        return str(date_str)


def time_ago(date_str):
    """Return a human-readable 'time ago' string."""
    if not date_str:
        return 'Unknown'
    try:
        dt = datetime.strptime(str(date_str)[:19], '%Y-%m-%d %H:%M:%S')
        diff = datetime.now() - dt
        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    except (ValueError, TypeError):
        return 'Unknown'


def generate_report_id(prefix='RPT'):
    """Generate a unique report ID."""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique = uuid.uuid4().hex[:4].upper()
    return f"{prefix}-{timestamp}-{unique}"

# 🔍 Campus Lost & Found Management System

A full-stack web application to help university students and staff report, track, and recover lost items on campus. Built with **Flask**, **Bootstrap 5**, **SQLite**, and **Matplotlib**.

---

## 📸 Features

| Feature | Description |
|---------|-------------|
| 🔐 Authentication | Register, login, logout with password hashing & sessions |
| 📝 Report Lost Items | Submit detailed reports with images and location |
| 🟢 Report Found Items | Log found items with deposit location |
| 🔎 Search & Filter | Search by keyword, category, status, and type |
| 🤖 Auto-Matching | Automatically matches lost & found items using Jaccard similarity |
| 🛡️ Admin Dashboard | Manage all reports, users, and manual matching |
| 📊 Analytics | Matplotlib charts — category, monthly trends, recovery rate |
| 🌙 Dark Mode | Toggle dark/light theme with localStorage persistence |
| 📱 Responsive | Mobile-friendly design with Bootstrap 5 |
| 🖼️ Image Upload | Upload item photos (max 5MB) |
| 📄 Pagination | Paginated search results |

---

## 🛠️ Tech Stack

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Database:** SQLite
- **Charts:** Matplotlib
- **Auth:** Werkzeug password hashing
- **Icons:** Bootstrap Icons

---

## 📁 Folder Structure

```
lost_found_system/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── templates/              # HTML templates
│   ├── base.html           # Base layout (navbar, footer, dark mode)
│   ├── index.html          # Landing page
│   ├── login.html          # Login form
│   ├── register.html       # Registration form
│   ├── dashboard.html      # User dashboard
│   ├── report_lost.html    # Report lost item form
│   ├── report_found.html   # Report found item form
│   ├── search.html         # Search & filter page
│   ├── admin_dashboard.html # Admin panel
│   ├── report_details.html # Item details + matches
│   ├── statistics.html     # Charts & analytics
│   └── profile.html        # User profile
├── static/
│   ├── css/style.css       # Custom CSS (glassmorphism, dark mode)
│   ├── js/script.js        # Client-side JavaScript
│   └── uploads/            # Uploaded item images
├── database/
│   └── lost_found.db       # SQLite database (auto-created)
└── utils/
    ├── __init__.py
    ├── auth.py             # Password hashing & validation
    ├── matching.py         # Auto-matching algorithm
    ├── reports.py          # Matplotlib chart generation
    └── helpers.py          # File upload, constants, utilities
```

---

## 🚀 How to Run

### 1. Install Python
Make sure Python 3.8+ is installed: https://python.org

### 2. Install Dependencies
```bash
cd lost_found_system
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
Navigate to: **http://127.0.0.1:5000**

### Demo Accounts
| Role | Email | Password |
|------|-------|----------|
| Admin | admin@campus.edu | admin123 |
| User | john@campus.edu | john123 |
| User | jane@campus.edu | jane123 |

---

## 🗄️ Database Tables

### users
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| full_name | TEXT | User's full name |
| email | TEXT | Unique email |
| department | TEXT | Department name |
| password_hash | TEXT | Hashed password (PBKDF2) |
| role | TEXT | 'user' or 'admin' |
| created_at | TIMESTAMP | Registration date |

### lost_items
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| report_id | TEXT | Unique report ID |
| user_id | INTEGER | Foreign key → users |
| item_name | TEXT | Name of lost item |
| category | TEXT | Item category |
| description | TEXT | Detailed description |
| last_seen_location | TEXT | Where it was last seen |
| date_lost | DATE | When it was lost |
| contact_info | TEXT | Contact details |
| image_path | TEXT | Uploaded image filename |
| status | TEXT | 'open', 'recovered', 'claimed', 'closed' |

### found_items
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| report_id | TEXT | Unique report ID |
| user_id | INTEGER | Foreign key → users |
| item_name | TEXT | Name of found item |
| category | TEXT | Item category |
| description | TEXT | Detailed description |
| found_location | TEXT | Where it was found |
| date_found | DATE | When it was found |
| deposited_at | TEXT | Where it was deposited |
| image_path | TEXT | Uploaded image filename |
| status | TEXT | 'open', 'returned', 'claimed', 'closed' |

### matches
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| lost_item_id | INTEGER | Foreign key → lost_items |
| found_item_id | INTEGER | Foreign key → found_items |
| match_score | REAL | Similarity score (0-100%) |
| status | TEXT | 'pending' or 'confirmed' |

---

## 🤖 Auto-Matching Algorithm

The matching system uses **Jaccard Similarity** with weighted scoring:

| Factor | Weight | Method |
|--------|--------|--------|
| Category | 30% | Exact match |
| Item Name | 25% | Jaccard similarity of word tokens |
| Description | 25% | Jaccard similarity of word tokens |
| Location | 20% | Jaccard similarity of word tokens |

**Formula:** `Jaccard(A, B) = |A ∩ B| / |A ∪ B|`

Matches scoring ≥20% are shown as possible matches.

---

## 📊 Module Explanations

### 1. app.py (Main Application)
- Configures Flask app, database, and routes
- Handles user authentication with session management
- CRUD operations for lost and found items
- Admin-only routes protected by decorators

### 2. utils/auth.py (Authentication)
- `hash_password()` — PBKDF2 hashing with salt
- `verify_password()` — Checks password against hash
- `sanitize_input()` — Removes HTML/script tags (XSS prevention)

### 3. utils/matching.py (Auto-Matching)
- `tokenize()` — Converts text to word token sets
- `jaccard_similarity()` — Calculates set similarity
- `calculate_match_score()` — Weighted multi-factor scoring
- `find_matches()` / `find_reverse_matches()` — Finds matching items

### 4. utils/reports.py (Charts)
- `generate_category_chart()` — Bar chart by category
- `generate_monthly_chart()` — Line chart of monthly trends
- `generate_status_pie()` — Donut chart of statuses
- `generate_recovery_chart()` — Gauge chart of recovery rate

### 5. utils/helpers.py (Utilities)
- File upload handling with UUID naming
- Date formatting and "time ago" display
- Constants (categories, locations, departments)

---

## ❓ Viva Questions & Answers

**Q1: What framework is used and why?**
Flask — lightweight Python web framework, easy to learn, modular, great for university projects.

**Q2: How are passwords stored?**
Using PBKDF2-SHA256 hashing with random salt via Werkzeug's `generate_password_hash()`. Plain-text passwords are never stored.

**Q3: How does the auto-matching work?**
Jaccard Similarity compares word tokens between lost and found items across 4 factors (category, name, description, location) with weighted scoring.

**Q4: What database is used?**
SQLite — serverless, file-based, zero configuration, ideal for small-to-medium applications.

**Q5: How is role-based access implemented?**
Custom decorators (`@login_required`, `@admin_required`) check the session before allowing access to protected routes.

**Q6: How are images handled?**
Images are uploaded via multipart forms, validated for extension, renamed with UUID, and stored in `static/uploads/`.

**Q7: What security measures are implemented?**
Password hashing, input sanitization (XSS prevention), session-based auth, file upload validation, CSRF via Flask-WTF.

**Q8: How are charts generated?**
Matplotlib generates charts server-side, encodes them as base64 PNG strings, and embeds them directly in HTML via `<img>` tags.

**Q9: What is glassmorphism?**
A UI design trend using semi-transparent backgrounds with blur effects (`backdrop-filter: blur()`) to create frosted glass appearances.

**Q10: How does dark mode work?**
JavaScript toggles a `data-theme` attribute on `<html>`. CSS variables change based on the theme. Preference is saved in `localStorage`.

---

## 📜 License

This project is for educational purposes (university mini-project submission).

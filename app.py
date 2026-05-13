"""
Campus Lost & Found Management System — Firebase Firestore Edition
"""
import os
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, session, jsonify)
from utils.auth import hash_password, verify_password, sanitize_input
from utils.matching import find_matches, find_reverse_matches
from utils.reports import (generate_category_chart, generate_monthly_chart,
                           generate_status_pie, generate_recovery_chart, get_statistics)
from utils.helpers import (CATEGORIES, LOCATIONS, DEPARTMENTS,
                           save_uploaded_image, format_date, time_ago, generate_report_id)
from utils.firebase_config import init_firebase, get_db

app = Flask(__name__)
app.secret_key = 'campus-lost-found-secret-key-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Firestore helpers ---
def doc_to_dict(doc):
    if not doc.exists:
        return None
    d = doc.to_dict()
    d['id'] = doc.id
    return d

def collection_list(name, order_field='created_at', direction='DESCENDING', limit=None, **filters):
    from google.cloud.firestore_v1.base_query import FieldFilter
    ref = get_db().collection(name)
    for k, v in filters.items():
        ref = ref.where(filter=FieldFilter(k, '==', v))
    ref = ref.order_by(order_field, direction=getattr(
        __import__('google.cloud.firestore_v1', fromlist=['Query']).Query, direction))
    if limit:
        ref = ref.limit(limit)
    return [doc_to_dict(d) for d in ref.stream()]

def collection_count(name, **filters):
    from google.cloud.firestore_v1.base_query import FieldFilter
    ref = get_db().collection(name)
    for k, v in filters.items():
        ref = ref.where(filter=FieldFilter(k, '==', v))
    return len(list(ref.stream()))

def get_doc(collection, doc_id):
    return doc_to_dict(get_db().collection(collection).document(doc_id).get())

def add_doc(collection, data):
    ts, ref = get_db().collection(collection).add(data)
    return ref.id

def update_doc(collection, doc_id, data):
    get_db().collection(collection).document(doc_id).update(data)

def delete_doc(collection, doc_id):
    get_db().collection(collection).document(doc_id).delete()

# --- Auth decorators ---
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# --- Template context ---
@app.context_processor
def inject_globals():
    return dict(categories=CATEGORIES, locations=LOCATIONS, departments=DEPARTMENTS,
                format_date=format_date, time_ago=time_ago, now=datetime.now())

# === PUBLIC ROUTES ===
@app.route('/')
def index():
    lost_count = collection_count('lost_items')
    found_count = collection_count('found_items')
    recovered = collection_count('lost_items', status='recovered')
    recent_lost = collection_list('lost_items', limit=6)
    recent_found = collection_list('found_items', limit=6)
    return render_template('index.html', lost_count=lost_count, found_count=found_count,
                           recovered=recovered, recent_lost=recent_lost, recent_found=recent_found)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = sanitize_input(request.form.get('full_name', ''))
        email = sanitize_input(request.form.get('email', '')).lower()
        dept = request.form.get('department', '')
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if not all([name, email, dept, password]):
            flash('All fields are required.', 'danger'); return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match.', 'danger'); return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger'); return redirect(url_for('register'))
        from google.cloud.firestore_v1.base_query import FieldFilter
        existing = list(get_db().collection('users').where(filter=FieldFilter('email', '==', email)).stream())
        if existing:
            flash('Email already registered.', 'danger'); return redirect(url_for('register'))
        add_doc('users', {'full_name': name, 'email': email, 'department': dept,
                          'password_hash': hash_password(password), 'role': 'user',
                          'created_at': datetime.now().isoformat()})
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = sanitize_input(request.form.get('email', '')).lower()
        password = request.form.get('password', '')
        from google.cloud.firestore_v1.base_query import FieldFilter
        docs = list(get_db().collection('users').where(filter=FieldFilter('email', '==', email)).stream())
        if docs:
            user = doc_to_dict(docs[0])
            if verify_password(user['password_hash'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['full_name']
                session['user_email'] = user['email']
                session['role'] = user['role']
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('admin_dashboard') if user['role'] == 'admin' else url_for('dashboard'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# === USER DASHBOARD ===
@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    my_lost = collection_list('lost_items', user_id=uid)
    my_found = collection_list('found_items', user_id=uid)
    stats = {'my_lost': len(my_lost), 'my_found': len(my_found),
             'my_recovered': sum(1 for i in my_lost if i['status'] == 'recovered'),
             'my_open': sum(1 for i in my_lost + my_found if i['status'] == 'open')}
    return render_template('dashboard.html', my_lost=my_lost, my_found=my_found, stats=stats)

@app.route('/profile')
@login_required
def profile():
    user = get_doc('users', session['user_id'])
    return render_template('profile.html', user=user)

# === LOST / FOUND ITEM ROUTES ===
@app.route('/report/lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        img = None
        if 'image' in request.files and request.files['image'].filename:
            img = save_uploaded_image(request.files['image'], app.config['UPLOAD_FOLDER'])
        add_doc('lost_items', {
            'report_id': generate_report_id('LOST'), 'user_id': session['user_id'],
            'item_name': sanitize_input(request.form['item_name']),
            'category': request.form['category'],
            'description': sanitize_input(request.form.get('description', '')),
            'last_seen_location': request.form.get('last_seen_location', ''),
            'date_lost': request.form.get('date_lost', ''),
            'contact_info': sanitize_input(request.form.get('contact_info', '')),
            'image_path': img, 'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()})
        flash('Lost item report submitted!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report_lost.html')

@app.route('/report/found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        img = None
        if 'image' in request.files and request.files['image'].filename:
            img = save_uploaded_image(request.files['image'], app.config['UPLOAD_FOLDER'])
        new_id = add_doc('found_items', {
            'report_id': generate_report_id('FOUND'), 'user_id': session['user_id'],
            'item_name': sanitize_input(request.form['item_name']),
            'category': request.form['category'],
            'description': sanitize_input(request.form.get('description', '')),
            'found_location': request.form.get('found_location', ''),
            'date_found': request.form.get('date_found', ''),
            'deposited_at': sanitize_input(request.form.get('deposited_at', '')),
            'image_path': img, 'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()})
        # Auto-match
        new_found = get_doc('found_items', new_id)
        if new_found:
            open_lost = collection_list('lost_items', status='open')
            for lost_item, score in find_reverse_matches(new_found, open_lost, threshold=20)[:5]:
                add_doc('matches', {'lost_item_id': lost_item['id'], 'found_item_id': new_id,
                                    'match_score': score, 'status': 'pending',
                                    'created_at': datetime.now().isoformat()})
        flash('Found item report submitted! Matches checked.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('report_found.html')

# === REPORT DETAILS / EDIT / DELETE / STATUS ===
@app.route('/report/<item_type>/<item_id>')
@login_required
def report_details(item_type, item_id):
    col = 'lost_items' if item_type == 'lost' else 'found_items'
    item = get_doc(col, item_id)
    if not item:
        flash('Report not found.', 'danger'); return redirect(url_for('dashboard'))
    reporter = get_doc('users', item['user_id'])
    matches_list = []
    if item_type == 'lost':
        matches_list = find_matches(item, collection_list('found_items', status='open'), 15)
    else:
        matches_list = find_reverse_matches(item, collection_list('lost_items', status='open'), 15)
    return render_template('report_details.html', item=item, item_type=item_type,
                           reporter=reporter, matches=matches_list)

@app.route('/report/<item_type>/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(item_type, item_id):
    col = 'lost_items' if item_type == 'lost' else 'found_items'
    item = get_doc(col, item_id)
    if not item or (item['user_id'] != session['user_id'] and session.get('role') != 'admin'):
        flash('Unauthorized.', 'danger'); return redirect(url_for('dashboard'))
    if request.method == 'POST':
        img = item.get('image_path')
        if 'image' in request.files and request.files['image'].filename:
            img = save_uploaded_image(request.files['image'], app.config['UPLOAD_FOLDER'])
        data = {'item_name': sanitize_input(request.form['item_name']),
                'category': request.form['category'],
                'description': sanitize_input(request.form.get('description', '')),
                'image_path': img, 'updated_at': datetime.now().isoformat()}
        if item_type == 'lost':
            data.update({'last_seen_location': request.form.get('last_seen_location', ''),
                         'date_lost': request.form.get('date_lost', ''),
                         'contact_info': sanitize_input(request.form.get('contact_info', ''))})
        else:
            data.update({'found_location': request.form.get('found_location', ''),
                         'date_found': request.form.get('date_found', ''),
                         'deposited_at': sanitize_input(request.form.get('deposited_at', ''))})
        update_doc(col, item_id, data)
        flash('Report updated!', 'success')
        return redirect(url_for('report_details', item_type=item_type, item_id=item_id))
    tpl = 'report_lost.html' if item_type == 'lost' else 'report_found.html'
    return render_template(tpl, item=item, editing=True)

@app.route('/report/<item_type>/<item_id>/delete', methods=['POST'])
@login_required
def delete_report(item_type, item_id):
    col = 'lost_items' if item_type == 'lost' else 'found_items'
    item = get_doc(col, item_id)
    if not item or (item['user_id'] != session['user_id'] and session.get('role') != 'admin'):
        flash('Unauthorized.', 'danger'); return redirect(url_for('dashboard'))
    delete_doc(col, item_id)
    flash('Report deleted.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/report/<item_type>/<item_id>/status', methods=['POST'])
@login_required
def update_status(item_type, item_id):
    col = 'lost_items' if item_type == 'lost' else 'found_items'
    item = get_doc(col, item_id)
    if not item or (item['user_id'] != session['user_id'] and session.get('role') != 'admin'):
        flash('Unauthorized.', 'danger'); return redirect(url_for('dashboard'))
    update_doc(col, item_id, {'status': request.form.get('status', 'open'),
                               'updated_at': datetime.now().isoformat()})
    flash('Status updated!', 'success')
    return redirect(url_for('report_details', item_type=item_type, item_id=item_id))

# === SEARCH ===
@app.route('/search')
@login_required
def search():
    keyword = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    status = request.args.get('status', '')
    item_type = request.args.get('type', 'all')
    page = int(request.args.get('page', 1))
    per_page = 9
    results = []
    for col, typ in [('lost_items', 'lost'), ('found_items', 'found')]:
        if item_type != 'all' and item_type != typ:
            continue
        items = collection_list(col)
        for item in items:
            item['type'] = typ
            if category and item.get('category') != category:
                continue
            if status and item.get('status') != status:
                continue
            if keyword:
                text = f"{item.get('item_name','')} {item.get('description','')}".lower()
                if keyword.lower() not in text:
                    continue
            results.append(item)
    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    total = len(results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    paginated = results[(page - 1) * per_page: page * per_page]
    return render_template('search.html', results=paginated, keyword=keyword,
                           selected_category=category, selected_status=status,
                           selected_type=item_type, page=page, total_pages=total_pages, total=total)

# === ADMIN ===
@app.route('/admin')
@admin_required
def admin_dashboard():
    lost = collection_list('lost_items')
    found = collection_list('found_items')
    users = collection_list('users')
    stats = get_statistics(lost, found)
    stats['total_users'] = len(users)
    matches_db = collection_list('matches', order_field='match_score')
    return render_template('admin_dashboard.html', lost_items=lost, found_items=found,
                           users=users, stats=stats, matches=matches_db)

@app.route('/admin/user/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session['user_id']:
        flash('Cannot delete yourself.', 'danger'); return redirect(url_for('admin_dashboard'))
    for col in ['lost_items', 'found_items']:
        for item in collection_list(col, user_id=user_id):
            delete_doc(col, item['id'])
    delete_doc('users', user_id)
    flash('User deleted.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/report/<item_type>/<item_id>/delete', methods=['POST'])
@admin_required
def admin_delete_report(item_type, item_id):
    col = 'lost_items' if item_type == 'lost' else 'found_items'
    delete_doc(col, item_id)
    flash('Report deleted by admin.', 'info')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/match/<lost_id>/<found_id>', methods=['POST'])
@admin_required
def manual_match(lost_id, found_id):
    update_doc('lost_items', lost_id, {'status': 'recovered', 'updated_at': datetime.now().isoformat()})
    update_doc('found_items', found_id, {'status': 'returned', 'updated_at': datetime.now().isoformat()})
    add_doc('matches', {'lost_item_id': lost_id, 'found_item_id': found_id,
                        'match_score': 100.0, 'status': 'confirmed',
                        'created_at': datetime.now().isoformat()})
    flash('Items matched!', 'success')
    return redirect(url_for('admin_dashboard'))

# === STATISTICS ===
@app.route('/statistics')
@login_required
def statistics():
    lost = collection_list('lost_items')
    found = collection_list('found_items')
    stats = get_statistics(lost, found)
    return render_template('statistics.html', stats=stats,
                           chart_category=generate_category_chart(lost, found),
                           chart_monthly=generate_monthly_chart(lost, found),
                           chart_status=generate_status_pie(lost, found),
                           chart_recovery=generate_recovery_chart(lost))

# === ENSURE ADMIN EXISTS ===
def ensure_admin():
    """Create admin account if it doesn't exist yet."""
    from google.cloud.firestore_v1.base_query import FieldFilter
    if list(get_db().collection('users').where(filter=FieldFilter('email', '==', 'admin@campus.edu')).stream()):
        return
    add_doc('users', {'full_name': 'Admin', 'email': 'admin@campus.edu', 'department': 'Admin Office',
                      'password_hash': hash_password('admin123'), 'role': 'admin',
                      'created_at': datetime.now().isoformat()})
    print("[OK] Admin account created: admin@campus.edu / admin123")

# Initialize Firebase at module level (works with both python app.py and gunicorn)
init_firebase()
ensure_admin()

if __name__ == '__main__':
    print("\n=== Campus Lost & Found (Firebase) ===")
    print("Open: http://127.0.0.1:5000")
    print("Admin: admin@campus.edu / admin123")
    print("======================================\n")
    app.run(debug=True, port=5000)



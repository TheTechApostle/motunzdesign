from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import json, os, uuid, time
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'motunz-secret-2025-very-secure'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXT = {'jpg', 'jpeg', 'png', 'webp', 'gif'}
DATA_FILE = 'data.json'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "admin": {
                "username": "admin",
                "password": generate_password_hash("motunz2025")
            },
            "products": [
                {"id":"p1","name":"Red Sequin Turban Cap","cat":"women","price":"₦12,000","img":"/static/img/img1.jpg","desc":"Pre-tied stretch turban with silver floral trim. Owambe-ready.","date":"2025-01-01"},
                {"id":"p2","name":"Striped Kufi Cap","cat":"men","price":"₦8,500","img":"/static/img/img2.jpg","desc":"Woven aso-oke kufi cap for traditional occasions.","date":"2025-01-01"},
                {"id":"p3","name":"Gold Lace Fascinator","cat":"fascinator","price":"₦25,000","img":"/static/img/img3.jpg","desc":"Wide brim lace fascinator with silver feather & floral accent.","date":"2025-01-01"},
                {"id":"p4","name":"Champagne Auto Gele","cat":"gele","price":"₦18,000","img":"/static/img/img4.jpg","desc":"Premium pre-tied auto gele with beaded embroidery.","date":"2025-01-01"},
                {"id":"p5","name":"Aso-oke Sculptor Cap","cat":"men","price":"₦10,000","img":"/static/img/img2.jpg","desc":"Tall structured woven cap for grooms & aso-ebi events.","date":"2025-01-01"},
                {"id":"p6","name":"Violet Turban Cap","cat":"women","price":"Contact Us","img":"/static/img/img1.jpg","desc":"Pleated turban with metallic trim. Available in all colours.","date":"2025-01-01"},
            ],
            "messages": [
                {"id":"m1","name":"Amara Okafor","phone":"08012345678","subject":"Auto Gele Order","message":"Hi, I need 10 pieces of auto gele in royal blue for my sister's wedding on Sept 20.","date":"2025-06-09 10:30","read":False},
                {"id":"m2","name":"Blessing Adeyemi","phone":"08023456789","subject":"Corporate Training Enquiry","message":"We have 25 girls at our skill centre in Surulere and would like to arrange training.","date":"2025-06-09 07:15","read":False},
                {"id":"m3","name":"Tunde Alade","phone":"08034567890","subject":"Men's Cap – Traditional Wedding","message":"I need 6 matching kufi caps in dark green aso-oke for a traditional wedding.","date":"2025-06-08 18:00","read":False},
                {"id":"m4","name":"Chisom Nwosu","phone":"08045678901","subject":"Thank you!","message":"Just got my turban caps, they're absolutely beautiful! Will definitely order again.","date":"2025-06-07 12:00","read":True},
            ],
            "orders": [
                {"id":"o7","client":"Amara Okafor","product":"Champagne Auto Gele","amount":"₦18,000","date":"2025-06-09","status":"new"},
                {"id":"o6","client":"Blessing Adeyemi","product":"Gold Fascinator","amount":"₦25,000","date":"2025-06-09","status":"processing"},
                {"id":"o5","client":"Chisom Nwosu","product":"Red Turban Cap × 3","amount":"₦36,000","date":"2025-06-08","status":"completed"},
                {"id":"o4","client":"Tunde Alade","product":"Striped Kufi Cap","amount":"₦8,500","date":"2025-06-08","status":"completed"},
                {"id":"o3","client":"Funmi Bello","product":"Private Training","amount":"TBD","date":"2025-06-07","status":"processing"},
            ],
            "slider": [
                {"id":"s1","img":"/static/img/img4.jpg","tag":"New Collection","title":"Wear Your Crown","title2":"with Confidence","sub":"Handcrafted turban caps, auto gele, fascinators & more — made with love in Lagos.","btn1":"Explore Collection","btn2":"Join Training"},
                {"id":"s2","img":"/static/img/img1.jpg","tag":"Turban Caps","title":"Red, Bold &","title2":"Unforgettable","sub":"Pre-tied elegance — slip on and step out in seconds.","btn1":"Shop Now","btn2":""},
                {"id":"s3","img":"/static/img/img3.jpg","tag":"Fascinators","title":"Statement Pieces","title2":"for Special Days","sub":"Weddings, owambe, corporate events — we dress your head for every occasion.","btn1":"Explore Styles","btn2":""},
                {"id":"s4","img":"/static/img/img2.jpg","tag":"Men's Collection","title":"Nigerian Pride","title2":"on Every Head","sub":"Aso-oke caps, kufi & custom woven designs for the modern Nigerian man.","btn1":"Shop Men's","btn2":""},
            ]
        }
    with open(DATA_FILE) as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ── PUBLIC ROUTES ─────────────────────────────────────────────────────────────
@app.route('/')
def index():
    data = load_data()
    products = data['products']
    slider = data['slider']
    return render_template('index.html', products=products, slider=slider)

@app.route('/api/products')
def api_products():
    data = load_data()
    cat = request.args.get('cat', 'all')
    products = data['products']
    if cat != 'all':
        products = [p for p in products if p['cat'] == cat]
    return jsonify(products)

@app.route('/contact', methods=['POST'])
def contact():
    data = load_data()
    msg = {
        "id": "m" + str(uuid.uuid4())[:8],
        "name": request.form.get('name','').strip(),
        "phone": request.form.get('phone','').strip(),
        "subject": request.form.get('subject','General Inquiry'),
        "message": request.form.get('message','').strip(),
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "read": False
    }
    if not msg['name'] or not msg['message']:
        return jsonify({"ok": False, "error": "Name and message are required."})
    data['messages'].insert(0, msg)
    save_data(data)
    return jsonify({"ok": True})

# ── ADMIN LOGIN ───────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        data = load_data()
        username = request.form.get('username','').strip()
        password = request.form.get('password','')
        if username == data['admin']['username'] and check_password_hash(data['admin']['password'], password):
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        error = 'Incorrect username or password.'
        time.sleep(0.8)  # brute-force delay
    return render_template('login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# ── ADMIN PAGES ───────────────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_dashboard():
    data = load_data()
    unread = sum(1 for m in data['messages'] if not m['read'])
    new_orders = sum(1 for o in data['orders'] if o['status'] == 'new')
    return render_template('admin.html',
        page='dashboard',
        products=data['products'],
        messages=data['messages'],
        orders=data['orders'],
        slider=data['slider'],
        unread=unread,
        new_orders=new_orders,
        stats={
            'products': len(data['products']),
            'messages': len(data['messages']),
            'unread': unread,
            'orders': len(data['orders']),
            'new_orders': new_orders,
        }
    )

@app.route('/admin/products')
@admin_required
def admin_products():
    data = load_data()
    return render_template('admin.html', page='products', products=data['products'],
        messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=sum(1 for m in data['messages'] if not m['read']),
        new_orders=sum(1 for o in data['orders'] if o['status']=='new'), stats={'products':len(data['products']),'messages':len(data['messages']),'unread':sum(1 for m in data['messages'] if not m['read']),'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

@app.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload():
    data = load_data()
    success = error = None
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        cat = request.form.get('cat','')
        price = request.form.get('price','Contact Us').strip()
        desc = request.form.get('desc','').strip()
        file = request.files.get('image')
        if not name or not cat:
            error = 'Product name and category are required.'
        elif not file or not allowed_file(file.filename):
            error = 'Please upload a valid image (JPG, PNG, WebP).'
        else:
            ext = file.filename.rsplit('.', 1)[1].lower()
            fname = f"{uuid.uuid4().hex}.{ext}"
            fpath = os.path.join(UPLOAD_FOLDER, fname)
            file.save(fpath)
            product = {
                "id": "p" + uuid.uuid4().hex[:8],
                "name": name,
                "cat": cat,
                "price": price or "Contact Us",
                "img": f"/static/uploads/{fname}",
                "desc": desc or "Handcrafted by Motunz Designs.",
                "date": datetime.now().strftime('%Y-%m-%d')
            }
            data['products'].insert(0, product)
            save_data(data)
            success = f'"{name}" added to catalogue!'
    return render_template('admin.html', page='upload', success=success, error=error,
        products=data['products'], messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=sum(1 for m in data['messages'] if not m['read']),
        new_orders=sum(1 for o in data['orders'] if o['status']=='new'),
        stats={'products':len(data['products']),'messages':len(data['messages']),'unread':sum(1 for m in data['messages'] if not m['read']),'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

@app.route('/admin/product/delete/<pid>', methods=['POST'])
@admin_required
def delete_product(pid):
    data = load_data()
    prod = next((p for p in data['products'] if p['id'] == pid), None)
    if prod:
        # remove uploaded file if it exists
        if '/uploads/' in prod['img']:
            try: os.remove(prod['img'].lstrip('/'))
            except: pass
        data['products'] = [p for p in data['products'] if p['id'] != pid]
        save_data(data)
    return redirect(url_for('admin_products'))

@app.route('/admin/messages')
@admin_required
def admin_messages():
    data = load_data()
    # mark all as read
    for m in data['messages']: m['read'] = True
    save_data(data)
    return render_template('admin.html', page='messages',
        products=data['products'], messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=0, new_orders=sum(1 for o in data['orders'] if o['status']=='new'),
        stats={'products':len(data['products']),'messages':len(data['messages']),'unread':0,'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

@app.route('/admin/orders')
@admin_required
def admin_orders():
    data = load_data()
    return render_template('admin.html', page='orders',
        products=data['products'], messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=sum(1 for m in data['messages'] if not m['read']),
        new_orders=sum(1 for o in data['orders'] if o['status']=='new'),
        stats={'products':len(data['products']),'messages':len(data['messages']),'unread':sum(1 for m in data['messages'] if not m['read']),'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

@app.route('/admin/order/status/<oid>', methods=['POST'])
@admin_required
def update_order_status(oid):
    data = load_data()
    status = request.form.get('status')
    for o in data['orders']:
        if o['id'] == oid:
            o['status'] = status
    save_data(data)
    return redirect(url_for('admin_orders'))

@app.route('/admin/slider', methods=['GET', 'POST'])
@admin_required
def admin_slider():
    data = load_data()
    success = error = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            tag = request.form.get('tag','').strip()
            title = request.form.get('title','').strip()
            title2 = request.form.get('title2','').strip()
            sub = request.form.get('sub','').strip()
            btn1 = request.form.get('btn1','Explore').strip()
            btn2 = request.form.get('btn2','').strip()
            file = request.files.get('image')
            if not title or not file or not allowed_file(file.filename):
                error = 'Title and image are required.'
            else:
                ext = file.filename.rsplit('.', 1)[1].lower()
                fname = f"slide_{uuid.uuid4().hex[:8]}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, fname))
                data['slider'].append({
                    "id": "s" + uuid.uuid4().hex[:6],
                    "img": f"/static/uploads/{fname}",
                    "tag": tag, "title": title, "title2": title2,
                    "sub": sub, "btn1": btn1, "btn2": btn2
                })
                save_data(data)
                success = 'Slide added!'
        elif action == 'delete':
            sid = request.form.get('sid')
            slide = next((s for s in data['slider'] if s['id']==sid), None)
            if slide and '/uploads/' in slide['img']:
                try: os.remove(slide['img'].lstrip('/'))
                except: pass
            data['slider'] = [s for s in data['slider'] if s['id'] != sid]
            save_data(data)
            success = 'Slide removed.'
    return render_template('admin.html', page='slider', success=success, error=error,
        products=data['products'], messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=sum(1 for m in data['messages'] if not m['read']),
        new_orders=sum(1 for o in data['orders'] if o['status']=='new'),
        stats={'products':len(data['products']),'messages':len(data['messages']),'unread':sum(1 for m in data['messages'] if not m['read']),'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    data = load_data()
    success = error = None
    if request.method == 'POST':
        cur = request.form.get('current_pass','')
        new_p = request.form.get('new_pass','')
        conf = request.form.get('confirm_pass','')
        if not check_password_hash(data['admin']['password'], cur):
            error = 'Current password is incorrect.'
        elif new_p != conf or len(new_p) < 6:
            error = "Passwords don't match or too short (min 6 chars)."
        else:
            data['admin']['password'] = generate_password_hash(new_p)
            save_data(data)
            success = 'Password updated successfully!'
    return render_template('admin.html', page='settings', success=success, error=error,
        products=data['products'], messages=data['messages'], orders=data['orders'], slider=data['slider'],
        unread=sum(1 for m in data['messages'] if not m['read']),
        new_orders=sum(1 for o in data['orders'] if o['status']=='new'),
        stats={'products':len(data['products']),'messages':len(data['messages']),'unread':sum(1 for m in data['messages'] if not m['read']),'orders':len(data['orders']),'new_orders':sum(1 for o in data['orders'] if o['status']=='new')})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

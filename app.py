from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import psycopg2.extras
from functools import wraps
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/images/produk'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zazab_supersecret123")  # Ganti dengan kunci rahasia yang kuat
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Database connection
DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    db = psycopg2.connect(DATABASE_URL, sslmode='require')
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
except Exception as e:
    print("Database connection error:", e)
    db = None


# Decorator untuk mewajibkan login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- USER ROUTES ----------------
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    cursor.execute("SELECT * FROM about")
    data = cursor.fetchall()
    return render_template('about.html', about=data)

@app.route('/contact')
def contact():
    cursor.execute("SELECT * FROM contact")
    data = cursor.fetchall()
    return render_template('contact.html', contact=data)

@app.route('/produk')
def produk():
    cursor.execute("SELECT * FROM produk")
    produk = cursor.fetchall()
    return render_template('produk.html', produk=produk)

# ---------------- LOGIN / LOGOUT ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password salah.')
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('login'))

# ---------------- ADMIN ROUTES ----------------
@app.route('/admin')
@login_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/produk', methods=['GET', 'POST'])
@login_required
def admin_produk():
    if request.method == 'POST':
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        harga = request.form['harga']
        file = request.files['gambar']

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        else:
            filename = None

        cursor.execute(
            "INSERT INTO produk (nama, deskripsi, harga, gambar) VALUES (%s, %s, %s, %s)",
            (nama, deskripsi, harga, filename)
        )
        db.commit()
        return redirect(url_for('admin_produk'))

    cursor.execute("SELECT * FROM produk")
    data = cursor.fetchall()
    return render_template('admin/produk_crud.html', produk=data)

@app.route('/admin/produk/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_produk(id):
    if request.method == 'POST':
        nama = request.form['nama']
        deskripsi = request.form['deskripsi']
        harga = request.form['harga']
        file = request.files.get('gambar')  # ✅ gunakan .get untuk aman

        # Ambil gambar lama
        cursor.execute("SELECT gambar FROM produk WHERE id=%s", (id,))
        old = cursor.fetchone()
        filename = old['gambar']

        # Jika upload gambar baru
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cursor.execute(
            "UPDATE produk SET nama=%s, deskripsi=%s, harga=%s, gambar=%s WHERE id=%s",
            (nama, deskripsi, harga, filename, id)
        )
        db.commit()
        return redirect(url_for('admin_produk'))

    cursor.execute("SELECT * FROM produk WHERE id=%s", (id,))
    produk = cursor.fetchone()
    return render_template('admin/edit_produk.html', produk=produk)



@app.route('/admin/produk/delete/<int:id>')
@login_required
def delete_produk(id):
    cursor.execute("SELECT gambar FROM produk WHERE id=%s", (id,))
    produk = cursor.fetchone()
    if produk and produk['gambar']:
        path = os.path.join(UPLOAD_FOLDER, produk['gambar'])
        if os.path.exists(path):
            os.remove(path)
    cursor.execute("DELETE FROM produk WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_produk'))


@app.route('/admin/about', methods=['GET', 'POST'])
@login_required
def admin_about():
    if request.method == 'POST':
        konten = request.form['konten']
        cursor.execute("INSERT INTO about (konten) VALUES (%s)", (konten,))
        db.commit()
    cursor.execute("SELECT * FROM about")
    about = cursor.fetchall()
    return render_template('admin/about_crud.html', about=about)

@app.route('/admin/about/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_about(id):
    if request.method == 'POST':
        konten = request.form['konten']
        cursor.execute("UPDATE about SET konten=%s WHERE id=%s", (konten, id))
        db.commit()
        return redirect(url_for('admin_about'))
    cursor.execute("SELECT * FROM about WHERE id=%s", (id,))
    about = cursor.fetchone()
    return render_template('admin/edit_about.html', about=about)

@app.route('/admin/about/delete/<int:id>')
@login_required
def delete_about(id):
    cursor.execute("DELETE FROM about WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_about'))

@app.route('/admin/contact', methods=['GET', 'POST'])
@login_required
def admin_contact():
    if request.method == 'POST':
        alamat = request.form['alamat']
        telepon = request.form['telepon']
        email = request.form['email']
        cursor.execute("INSERT INTO contact (alamat, telepon, email) VALUES (%s, %s, %s)", (alamat, telepon, email))
        db.commit()
    cursor.execute("SELECT * FROM contact")
    contact = cursor.fetchall()
    return render_template('admin/contact_crud.html', contact=contact)

@app.route('/admin/contact/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    if request.method == 'POST':
        alamat = request.form['alamat']
        telepon = request.form['telepon']
        email = request.form['email']
        cursor.execute("UPDATE contact SET alamat=%s, telepon=%s, email=%s WHERE id=%s", (alamat, telepon, email, id))
        db.commit()
        return redirect(url_for('admin_contact'))
    cursor.execute("SELECT * FROM contact WHERE id=%s", (id,))
    contact = cursor.fetchone()
    return render_template('admin/edit_contact.html', contact=contact)

@app.route('/admin/contact/delete/<int:id>')
@login_required
def delete_contact(id):
    cursor.execute("DELETE FROM contact WHERE id=%s", (id,))
    db.commit()
    return redirect(url_for('admin_contact'))

# ----------------- MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)

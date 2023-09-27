from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from pymongo import MongoClient
from dotenv import load_dotenv
import string
import random
import os
from os.path import join, dirname
from datetime import datetime

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =   os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def generate_random_filename(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/imgs/lampiran'
app.secret_key = os.urandom(7)

@app.route('/')
def index():
    page = "Lapor LX"
    total_d = db.laporan.count_documents({})
    
    return render_template('index.html', page=page, total_d=total_d)

@app.route('/laporan')
def form():
    page = "Buat Laporan"
    return render_template('form.html', page=page)

@app.route('/submit', methods=['POST'])
def submit():
    page = "Buat Laporan"
    if request.method == 'POST':
        id_person = generate_random_filename(6)
        nama = request.form['nama']
        no_wa = request.form['no-wa']
        id_discord = request.form['id-discord']
        jenis_l = request.form['jenis-l']
        laporan = request.form['laporan']
        lampiran = request.files['lampiran']
        filename = None
        tanggal = datetime.now().strftime("%Y-%m-%d")
        status = 'Belum'

        if lampiran:
            filename = generate_random_filename(10) + '.jpg'
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            lampiran.save(filepath)

        if not nama or not no_wa or not id_discord or not jenis_l or not laporan or not lampiran:
            flash('Harap mengisi semua form dengan benar.', 'error')
            return redirect(url_for('form'))

        data = {
            'id_person': id_person,
            'nama': nama,
            'no_wa': no_wa,
            'id_discord': id_discord,
            'jenis_l': jenis_l,
            'laporan': laporan,
            'lampiran': filename,
            'status': status,
            'tanggal': tanggal
        }

        session['kode_akses'] = id_person

        db.laporan.insert_one(data)
        
    
    if 'kode_akses' in session:
        flash('Laporan Anda telah dikirim!', 'success')
        return render_template('form.html', kode_akses=id_person, page=page)
    else:
        return redirect(url_for('form'))
    
@app.route('/cari-laporan')
def c_laporan():
    page = 'Cari Laporan'
    return render_template('s-lapor.html', page=page)

@app.route('/cari-laporan/hasil', methods=['POST'])
def cari():
    page = 'Cari Laporan'
    kode_akses = request.form['id_person']

    data = db.laporan.find_one({'id_person': kode_akses})

    session['kode_akses'] = kode_akses

    if data :
        session['kode_akses'] = True
        return render_template('s-lapor.html', data=data, id_person=kode_akses, page=page)
    else:
        flash('Data laporan tidak ada.', 'error')
        return redirect(url_for('c_laporan'))

@app.route('/login')
def login():
    page = "Sign In"
    return render_template('admin/login.html', page=page)

@app.route('/login/auth', methods=['GET', 'POST'])
def login_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Isi kedua kolom username dan password.', 'error')
            return redirect(url_for('login'))

        user = db.admin.find_one({'username': username, 'password': password})

        if user:
            session['logged_in'] = True
            key = generate_random_filename(8)

            return redirect(url_for('dashboard', key=key))
        else:
            flash('Username atau Password yang anda masukan salah. Silahkan coba lagi.', 'error')
            return redirect(url_for('login'))
        


@app.route('/dashboard/<key>')
def dashboard(key):
    page = "Dashboard"
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('admin/dashboard.html', data=data, key=key, page=page)

@app.route('/get_data/<key>/<id_person>')
def get_data(key, id_person):
    page = "Dashboard"

    laporan = db.laporan.find_one({"id_person": id_person}, {'_id': False})

    data = list(db.laporan.find({}, {'_id': False}))
    
    return render_template('componens/db/card-laporan.html', data=data, selected_laporan=laporan, key=key, page=page)
    
@app.route('/update_status/<id_person>', methods=['POST'])
def update_status(id_person):
    page = "Dashboard"
    new_status = 'Sudah'
    db.laporan.update_one({'id_person': id_person}, {'$set': {'status': new_status}})
    return redirect(url_for('dashboard', key=id_person, page=page))


@app.route('/analisis/<key>')
def analisis(key):
    page = "Analisis"
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    total_d = db.laporan.count_documents({})
    t_belum = db.laporan.count_documents({"status": "Belum"})
    t_sudah = db.laporan.count_documents({"status": "Sudah"})
    
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('admin/analisis.html', data=data, key=key,total_d=total_d, t_belum=t_belum, t_sudah=t_sudah, page=page)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
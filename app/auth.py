from flask import Blueprint, render_template, render_template, jsonify, request, redirect, url_for, flash, session, current_app
from pymongo import MongoClient
from dotenv import load_dotenv
import string
import random
import os
from os.path import join, dirname
from datetime import datetime
import hashlib

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# MONGODB_URI = os.environ.get("MONGODB_URI")
# DB_NAME =   os.environ.get("DB_NAME")

# client = MongoClient(MONGODB_URI)
# db = client[DB_NAME]

client = MongoClient("mongodb://laporlx:pkl123@ac-gf9nitl-shard-00-00.y5cgdlb.mongodb.net:27017,ac-gf9nitl-shard-00-01.y5cgdlb.mongodb.net:27017,ac-gf9nitl-shard-00-02.y5cgdlb.mongodb.net:27017/?ssl=true&replicaSet=atlas-cspp58-shard-0&authSource=admin&retryWrites=true&w=majority")
db = client.lapor_lx

def generate_random_filename(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/add-access-admin/<key>', methods=['POST'])  
def add_admin(key):
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        doc = {
            "nama": name,
            "username": username, 
            "password": password_hash,    
        }
        user = db.admin.insert_one(doc)

        if user:
            flash('Akses telah ditambahkan.', 'success')
            return redirect(url_for('main.admin_access', key=key))
        else:
            flash('Akses gagal ditambahkan.', 'error')
            return redirect(url_for('main.admin_access', key=key))

@auth_bp.route('/submit', methods=['POST'])
def submit():
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

        allowed_extensions = {'png', 'jpg', 'jpeg'}

        if lampiran and lampiran.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
            filename = generate_random_filename(10) + '.jpg'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            lampiran.save(filepath)
        else :
            flash('Lampiran harus berupa gambar.', 'error')
            return redirect(url_for('main.report'))

        if not nama or not no_wa or not id_discord or not jenis_l or not laporan or not lampiran:
            flash('Harap mengisi semua form dengan benar.', 'error')
            return redirect(url_for('main.report'))

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

        add = db.laporan.insert_one(data)
        if add:
            flash('Laporan Anda telah dikirim!', 'success')
            key = generate_random_filename(12)
            return redirect(url_for('main.access_code', key=key, kode_akses=id_person))
        else:
            flash('Username atau Password yang anda masukan salah. Silahkan coba lagi.', 'error')
            return redirect(url_for('main.report'))

@auth_bp.route('/tracking/result', methods=['POST'])
def cari():
    page = 'Tracking'
    kode_akses = request.form['id_person']
    
    if not kode_akses :
      flash('Harap masukkan data dengan benar', 'error')
      return redirect(url_for('main.tracking'))

    data = db.laporan.find_one({'id_person': kode_akses})
    session['kode_akses'] = kode_akses

    if data :
        session['kode_akses'] = True
        return render_template('report/tracking.html', data=data, id_person=kode_akses, page=page)
    else:
        flash('Data laporan tidak ada.', 'error')
        return redirect(url_for('main.tracking'))

@auth_bp.route('/login')
def login():
    page = 'Log In'
    return render_template('admin/login.html', page=page)

@auth_bp.route('/login/auth', methods=['GET', 'POST'])
def login_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()

        if not username or not password:
            flash('Isi kedua kolom username dan password.', 'error')
            return redirect(url_for('auth.login'))

        user = db.admin.find_one({'username': username, 'password': password})

        if user:
            session['logged_in'] = True
            key = generate_random_filename(18)
            return redirect(url_for('main.dashboard', key=key))
        else:
            flash('Username atau Password yang anda masukan salah. Silahkan coba lagi.', 'error')
            return redirect(url_for('auth.login'))
  
@auth_bp.route('/get_data/<key>/<id_person>')
def get_data(key, id_person):
    page = "Dashboard"

    laporan = db.laporan.find_one({"id_person": id_person}, {'_id': False})

    data = list(db.laporan.find({}, {'_id': False}))
    
    return render_template('admin/temp/card-info.html', data=data, selected_laporan=laporan, key=key, page=page)

@auth_bp.route('/update_status/<id_person>', methods=['POST'])
def update_status(id_person):
    page = "Dashboard"
    new_status = 'Sudah'
    if request.method == 'POST':
        feedback = request.form['feedback']
        nama_teknisi = request.form['nama-teknisi']

        if not feedback or not nama_teknisi :
            flash('Harap mengisi semua form dengan benar.', 'error')
        
        db.laporan.update_one(
            {'id_person': id_person},
            {
                '$set': {
                    'status': new_status,
                    'feedback': feedback,
                    'nama_teknisi': nama_teknisi
                }
            },
            upsert=True
        )
        
        flash('Feedback telah dikirim!', 'success')
        return redirect(url_for('main.workspace', key=id_person, page=page))

@auth_bp.route('/delete/<key>/<id_person>')
def delete(key, id_person):
    record = db.laporan.find_one({"id_person": id_person})
    if record:
        lampiran_path = os.path.join(current_app.config['UPLOAD_FOLDER'], record['lampiran'])
        if os.path.exists(lampiran_path):
            os.remove(lampiran_path)

        result = db.laporan.delete_one({"id_person": id_person})

        if result.deleted_count == 1:
            flash('Laporan telah dihapus!', 'success')
        else:
            flash('Laporan gagal dihapus!', 'error')
    else:
        flash('Laporan tidak ditemukan!', 'error')

    return redirect(url_for('main.dashboard', key=key))

@auth_bp.route('/delete-admin/<key>/<password>')
def delete_admin(key, password):
    record = db.admin.find_one({"password": password})
    if record:
        record = db.admin.delete_one({"password": password})

        if record.deleted_count == 1:
            flash('Akses telah dihapus!', 'success')
        else:
            flash('Akses gagal dihapus!', 'error')
    else:
        flash('Akses tidak ditemukan!', 'error')

    return redirect(url_for('main.admin_access', key=key))
    
@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('auth.login'))
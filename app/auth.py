from flask import Blueprint, render_template, render_template, jsonify, request, redirect, url_for, flash, session, current_app
from pymongo import MongoClient
from dotenv import load_dotenv
import string
import random
import os
from os.path import join, dirname
from datetime import datetime

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


@auth_bp.route('/submit', methods=['POST'])
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
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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
        return render_template('report/index.html', kode_akses=id_person, page=page)
    else:
        return redirect(url_for('report'))
    
@auth_bp.route('/tracking/result', methods=['POST'])
def cari():
    page = 'Tracking'
    kode_akses = request.form['id_person']

    data = db.laporan.find_one({'id_person': kode_akses})

    session['kode_akses'] = kode_akses

    if data :
        session['kode_akses'] = True
        return render_template('report/tracking.html', data=data, id_person=kode_akses, page=page)
    else:
        flash('Data laporan tidak ada.', 'error')
        return redirect(url_for('tracking'))

@auth_bp.route('/login')
def login():
    page = 'Log In'
    return render_template('admin/login.html', page=page)

@auth_bp.route('/login/auth', methods=['GET', 'POST'])
def login_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Isi kedua kolom username dan password.', 'error')
            return redirect(url_for('auth.login'))

        user = db.admin.find_one({'username': username, 'password': password})

        if user:
            session['logged_in'] = True
            key = generate_random_filename(8)
            flash('Anda berhasil Log In.', 'success')
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
            return redirect(url_for('main.dashboard', key=id_person))
        
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
        return redirect(url_for('main.dashboard', key=id_person))

@auth_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('auth.login'))


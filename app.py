from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
from pymongo import MongoClient
import string
import random
import os
from datetime import datetime

client = MongoClient('mongodb+srv://test:sparta@cluster0.mdmqvsh.mongodb.net/')
db = client.lapor_lx

def generate_random_filename(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/img/lampiran'
app.secret_key = os.urandom(7)

@app.route('/')
def index():
    total_d = db.laporan.count_documents({})
    return render_template('index.html', total_d=total_d)

@app.route('/laporan')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
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

        db.laporan.insert_one(data)

        flash('Laporan Anda telah dikirim!', 'success')
        return redirect(url_for('index'))

@app.route('/login')
def login():
    return render_template('admin/login.html')

@app.route('/login/auth', methods=['GET', 'POST'])
def login_auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Isi kedua kolom username dan password.', 'error')
            return redirect(url_for('login'))

        user = db.admin_user.find_one({'username': username, 'password': password})

        if user:
            flash('Login berhasil!', 'success')
            session['logged_in'] = True
            key = generate_random_filename(8)

            return redirect(url_for('dashboard', key=key))
        else:
            flash('Username atau Password yang anda masukan salah. Silahkan coba lagi.', 'error')
            return redirect(url_for('login'))
        


@app.route('/dashboard/<key>')
def dashboard(key):
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('admin/dashboard.html', data=data, key=key)

@app.route('/get_data/<key>/<key_person>')
def get_data(key_person, key):
    laporan = db.laporan.find_one({"id_person": key_person}, {'_id': False})
    data = list(db.laporan.find({}, {'_id': False}))
    
    return render_template('admin/dashboard.html', data=data, selected_laporan=laporan, key=key)
    
@app.route('/update_status/<key_person>', methods=['POST'])
def update_status(key_person):
    new_status = 'Sudah'
    db.laporan.update_one({'id_person': key_person}, {'$set': {'status': new_status}})
    return redirect(url_for('dashboard', key=key_person))


@app.route('/analisis/<key>')
def analisis(key):
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    total_d = db.laporan.count_documents({})
    t_belum = db.laporan.count_documents({"status": "Belum"})
    t_sudah = db.laporan.count_documents({"status": "Sudah"})
    
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('admin/analisis.html', data=data, key=key,total_d=total_d, t_belum=t_belum, t_sudah=t_sudah)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Anda telah logout.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
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

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    page = 'Home'
    total_d = db.laporan.count_documents({})
    return render_template('home.html', page=page, total_d=total_d)

@main_bp.route('/report')
def report():
    page = 'Report'
    return render_template('report/index.html', page=page)

@main_bp.route('/tracking')
def tracking():
    page = 'Tracking'
    return render_template('report/tracking.html', page=page)

@main_bp.route('/workspace/<key>')
def workspace(key):
    page = "Workspace"
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('auth.login'))
    
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('temp/index.html', data=data, key=key, page=page)

@main_bp.route('/dashboard/<key>')
def dashboard(key):
    page = "Dashboard"
    if not session.get('logged_in'):
        flash('Anda harus login terlebih dahulu!', 'error')
        return redirect(url_for('auth.login'))
    
    total_d = db.laporan.count_documents({})
    t_belum = db.laporan.count_documents({"status": "Belum"})
    t_sudah = db.laporan.count_documents({"status": "Sudah"})
    

    kategori = {
        'media':db.laporan.count_documents({"jenis_l": "Media"}),
        'text':db.laporan.count_documents({"jenis_l": "Text"}),
        'foto':db.laporan.count_documents({"jenis_l": "Foto"}),
        'video':db.laporan.count_documents({"jenis_l": "Video"}),
        'server':db.laporan.count_documents({"jenis_l": "Server"}),
        'pembayaran':db.laporan.count_documents({"jenis_l": "Pembayaran"}),
        'teknis':db.laporan.count_documents({"jenis_l": "Teknis atau Mentor"}),
    }
    data = list(db.laporan.find({}, {'_id': False}))
    return render_template('temp/index.html', data=data, key=key,total_d=total_d, t_belum=t_belum, t_sudah=t_sudah, page=page, kategori=kategori)


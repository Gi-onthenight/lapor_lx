from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/laporan')
def form():
    return render_template('form.html')

@app.route('/signin')
def signin():
    return render_template('admin/login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@app.route('/analisis')
def analisis():
    return render_template('admin/analisis.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
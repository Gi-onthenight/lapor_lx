from flask import Flask
from app.auth import auth_bp
from app.main import main_bp
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/lampiran'
app.secret_key = os.urandom(7)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
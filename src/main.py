from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

# إنشاء تطبيق Flask
app = Flask(__name__)

# تكوين قاعدة البيانات للإنتاج
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///employee_system.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد مفتاح سري للجلسات
app.secret_key = 'employee_management_system_secret_key'

# استيراد كائن قاعدة البيانات
from src.db import db  # import db from the new db.py file

# استيراد النماذج بعد استيراد كائن قاعدة البيانات
from src.models.branch import Branch
from src.models.employee import Employee

# استيراد وتسجيل مسارات التطبيق
from src.routes.branch import branch_bp
from src.routes.employee import employee_bp
from src.routes.search import search_bp
from src.routes.report import report_bp
from src.auth import init_auth

# تهيئة نظام المصادقة
init_auth(app)

app.register_blueprint(branch_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(search_bp)
app.register_blueprint(report_bp)

@app.route('/')
def index():
    """الصفحة الرئيسية للتطبيق"""
    return render_template('index.html')

db.init_app(app)  # initialize db with app

with app.app_context():
    """إنشاء جداول قاعدة البيانات"""
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

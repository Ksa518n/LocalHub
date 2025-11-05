#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LocalHub - نظام إدارة محلي متكامل
تطبيق Flask آمن يعمل محليًا على Termux
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
import os
import json
import logging
import zipfile
from datetime import datetime
import io

# إعداد التطبيق
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # حد أقصى 100MB

# المسارات الأساسية
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
BACKUP_FOLDER = os.path.join(BASE_DIR, 'backups')
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
TASKS_FILE = os.path.join(DATA_FOLDER, 'tasks.json')
KEY_FILE = os.path.join(DATA_FOLDER, 'secret.key')
LOG_FILE = os.path.join(BASE_DIR, 'local_hub.log')

# إعداد نظام التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ],
    force=True
)
logger = logging.getLogger(__name__)

# تأكد من أن السجلات تُكتب فورًا
for handler in logging.root.handlers:
    handler.flush()

# إنشاء المجلدات إذا لم تكن موجودة
for folder in [UPLOAD_FOLDER, BACKUP_FOLDER, DATA_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# ===== إدارة التشفير =====
def load_or_create_key():
    """تحميل أو إنشاء مفتاح التشفير"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        logger.info("تم إنشاء مفتاح تشفير جديد")
        return key

# تحميل مفتاح التشفير
ENCRYPTION_KEY = load_or_create_key()
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_file(file_data):
    """تشفير محتوى الملف"""
    return cipher.encrypt(file_data)

def decrypt_file(encrypted_data):
    """فك تشفير محتوى الملف"""
    return cipher.decrypt(encrypted_data)

# ===== إدارة المهام =====
def load_tasks():
    """تحميل المهام من الملف"""
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_tasks(tasks):
    """حفظ المهام إلى الملف"""
    with open(TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

# ===== المسارات (Routes) =====

@app.route('/')
def index():
    """الصفحة الرئيسية"""
    logger.info("تم الوصول إلى الصفحة الرئيسية")
    return render_template('index.html')

# ----- إدارة المهام -----
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """جلب جميع المهام"""
    tasks = load_tasks()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    """إضافة مهمة جديدة"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        
        if not title:
            return jsonify({'error': 'العنوان مطلوب'}), 400
        
        tasks = load_tasks()
        new_task = {
            'id': len(tasks) + 1,
            'title': title,
            'description': data.get('description', '').strip(),
            'due_date': data.get('due_date', ''),
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        
        tasks.append(new_task)
        save_tasks(tasks)
        logger.info(f"تمت إضافة مهمة جديدة: {title}")
        
        return jsonify(new_task), 201
    except Exception as e:
        logger.error(f"خطأ في إضافة مهمة: {str(e)}")
        return jsonify({'error': 'فشل في إضافة المهمة'}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """تحديث حالة المهمة"""
    try:
        data = request.get_json()
        tasks = load_tasks()
        
        for task in tasks:
            if task['id'] == task_id:
                task['completed'] = data.get('completed', task['completed'])
                save_tasks(tasks)
                logger.info(f"تم تحديث المهمة #{task_id}")
                return jsonify(task)
        
        return jsonify({'error': 'المهمة غير موجودة'}), 404
    except Exception as e:
        logger.error(f"خطأ في تحديث مهمة: {str(e)}")
        return jsonify({'error': 'فشل في تحديث المهمة'}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """حذف مهمة"""
    try:
        tasks = load_tasks()
        tasks = [t for t in tasks if t['id'] != task_id]
        save_tasks(tasks)
        logger.info(f"تم حذف المهمة #{task_id}")
        return jsonify({'message': 'تم حذف المهمة'}), 200
    except Exception as e:
        logger.error(f"خطأ في حذف مهمة: {str(e)}")
        return jsonify({'error': 'فشل في حذف المهمة'}), 500

# ----- إدارة الملفات -----
@app.route('/files', methods=['GET'])
def get_files():
    """جلب قائمة الملفات"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                # إزالة اللاحقة .encrypted من الاسم
                display_name = filename.replace('.encrypted', '')
                files.append({
                    'name': display_name,
                    'internal_name': filename,
                    'size': os.path.getsize(filepath),
                    'uploaded_at': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        files.sort(key=lambda x: x['uploaded_at'], reverse=True)
        return jsonify(files)
    except Exception as e:
        logger.error(f"خطأ في جلب الملفات: {str(e)}")
        return jsonify({'error': 'فشل في جلب الملفات'}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """رفع ملف جديد"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'لم يتم اختيار ملف'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'لم يتم اختيار ملف'}), 400
        
        # تأمين اسم الملف
        original_filename = secure_filename(file.filename)
        
        # قراءة محتوى الملف وتشفيره
        file_data = file.read()
        encrypted_data = encrypt_file(file_data)
        
        # حفظ الملف المشفر
        encrypted_filename = original_filename + '.encrypted'
        filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)
        
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)
        
        logger.info(f"تم رفع وتشفير ملف: {original_filename}")
        
        return jsonify({
            'message': 'تم رفع الملف بنجاح',
            'filename': original_filename,
            'size': len(file_data)
        }), 201
    except Exception as e:
        logger.error(f"خطأ في رفع ملف: {str(e)}")
        return jsonify({'error': 'فشل في رفع الملف'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """تحميل ملف"""
    try:
        # البحث عن الملف المشفر
        encrypted_filename = filename + '.encrypted'
        filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        # قراءة وفك تشفير الملف
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = decrypt_file(encrypted_data)
        
        logger.info(f"تم تحميل ملف: {filename}")
        logger.handlers[0].flush()  # تأكد من كتابة السجل فورًا
        
        # إرسال الملف المفكوك باسمه الأصلي
        return send_file(
            io.BytesIO(decrypted_data),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"خطأ في تحميل ملف: {str(e)}")
        logger.handlers[0].flush()  # تأكد من كتابة السجل فورًا
        return jsonify({'error': 'فشل في تحميل الملف'}), 500

@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    """حذف ملف"""
    try:
        encrypted_filename = filename + '.encrypted'
        filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'الملف غير موجود'}), 404
        
        os.remove(filepath)
        logger.info(f"تم حذف ملف: {filename}")
        
        return jsonify({'message': 'تم حذف الملف'}), 200
    except Exception as e:
        logger.error(f"خطأ في حذف ملف: {str(e)}")
        return jsonify({'error': 'فشل في حذف الملف'}), 500

# ----- النسخ الاحتياطي والسجلات -----
@app.route('/backup', methods=['POST'])
def create_backup():
    """إنشاء نسخة احتياطية"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        backup_filename = f'backup_{timestamp}.zip'
        backup_path = os.path.join(BACKUP_FOLDER, backup_filename)
        
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # إضافة جميع الملفات
            for filename in os.listdir(UPLOAD_FOLDER):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                if os.path.isfile(filepath):
                    zipf.write(filepath, os.path.join('uploads', filename))
            
            # إضافة ملف المهام
            if os.path.exists(TASKS_FILE):
                zipf.write(TASKS_FILE, 'data/tasks.json')
        
        logger.info(f"تم إنشاء نسخة احتياطية: {backup_filename}")
        
        return jsonify({
            'message': 'تم إنشاء النسخة الاحتياطية بنجاح',
            'filename': backup_filename,
            'size': os.path.getsize(backup_path)
        }), 201
    except Exception as e:
        logger.error(f"خطأ في إنشاء نسخة احتياطية: {str(e)}")
        return jsonify({'error': 'فشل في إنشاء النسخة الاحتياطية'}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """جلب السجلات"""
    try:
        if not os.path.exists(LOG_FILE):
            return jsonify({'logs': []})
        
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            # قراءة آخر 100 سطر
            lines = f.readlines()
            recent_logs = lines[-100:] if len(lines) > 100 else lines
        
        return jsonify({'logs': recent_logs})
    except Exception as e:
        logger.error(f"خطأ في جلب السجلات: {str(e)}")
        return jsonify({'error': 'فشل في جلب السجلات'}), 500

# ----- معالج الأخطاء -----
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'حجم الملف كبير جدًا (الحد الأقصى 100MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'الصفحة غير موجودة'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'خطأ في الخادم'}), 500

# ----- نقطة البداية -----
if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("بدء تشغيل LocalHub")
    logger.info("=" * 50)
    
    # التشغيل على الواجهة المحلية فقط لأسباب أمنية
    app.run(host='127.0.0.1', port=5000, debug=False)

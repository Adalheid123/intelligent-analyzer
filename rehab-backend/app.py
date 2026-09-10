"""
康复端后端主程序
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db, Doctor, Patient, Admin
from auth import generate_token
from routes.doctor import doctor_bp
from routes.patient import patient_bp
from routes.admin import admin_bp
import os

app = Flask(__name__)
CORS(app)

# 数据库配置
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///rehab.db')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 注册蓝图
app.register_blueprint(doctor_bp, url_prefix='/api/rehab/doctor')
app.register_blueprint(patient_bp, url_prefix='/api/rehab/patient')
app.register_blueprint(admin_bp, url_prefix='/api/rehab/admin')


@app.route('/')
def index():
    return jsonify({'status': 'ok', 'service': 'rehab-backend'})


@app.route('/api/rehab/login', methods=['POST'])
def login():
    """统一登录接口"""
    data = request.get_json()
    role = data.get('role')
    password = data.get('password', '')

    if role == 'doctor':
        hospital = data.get('hospital', '').strip()
        name = data.get('doctorName', '').strip()
        doctor = Doctor.query.filter_by(hospital=hospital, name=name).first()
        if not doctor or not doctor.check_password(password):
            return jsonify({'success': False, 'error': '医院或医生姓名或密码错误'}), 401
        token = generate_token(doctor.id, 'doctor', {'hospital': hospital, 'name': name})
        return jsonify({'success': True, 'token': token, 'user': doctor.to_dict()})

    elif role == 'patient':
        hospital = data.get('hospital', '').strip()
        doctor_name = data.get('doctorName', '').strip()
        patient_name = data.get('patientName', '').strip()
        doctor = Doctor.query.filter_by(hospital=hospital, name=doctor_name).first()
        if not doctor:
            return jsonify({'success': False, 'error': '主治医生不存在'}), 401
        patient = Patient.query.filter_by(hospital=hospital, doctor_id=doctor.id, name=patient_name).first()
        if not patient or not patient.check_password(password):
            return jsonify({'success': False, 'error': '患者信息或密码错误'}), 401
        token = generate_token(patient.id, 'patient', {
            'hospital': hospital,
            'doctorName': doctor_name,
            'patientName': patient_name
        })
        return jsonify({'success': True, 'token': token, 'user': patient.to_dict()})

    elif role == 'admin':
        username = data.get('username', '').strip()
        admin = Admin.query.filter_by(username=username).first()
        if not admin or not admin.check_password(password):
            return jsonify({'success': False, 'error': '管理员账号或密码错误'}), 401
        token = generate_token(admin.id, 'admin', {'username': username})
        return jsonify({'success': True, 'token': token, 'user': {'username': username}})

    return jsonify({'success': False, 'error': '未知角色'}), 400


@app.route('/api/rehab/register', methods=['POST'])
def register():
    """注册接口（医生/患者）"""
    data = request.get_json()
    role = data.get('role')

    if role == 'doctor':
        hospital = data.get('hospital', '').strip()
        name = data.get('doctorName', '').strip()
        password = data.get('password', '123456')

        if not hospital or not name:
            return jsonify({'success': False, 'error': '信息不完整'}), 400

        exist = Doctor.query.filter_by(hospital=hospital, name=name).first()
        if exist:
            return jsonify({'success': False, 'error': '该医生已存在'}), 400

        doctor = Doctor(hospital=hospital, name=name)
        doctor.set_password(password)
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'success': True, 'doctor': doctor.to_dict()})

    return jsonify({'success': False, 'error': '暂只支持医生注册'}), 400


@app.route('/api/rehab/change-password', methods=['POST'])
def change_password():
    """修改密码"""
    from auth import token_required, decode_token
    data = request.get_json()
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = decode_token(token)
    if not payload:
        return jsonify({'success': False, 'error': '未登录'}), 401

    role = payload['role']
    user_id = payload['user_id']
    old_pwd = data.get('oldPassword', '')
    new_pwd = data.get('newPassword', '')

    if role == 'doctor':
        user = Doctor.query.get(user_id)
    elif role == 'patient':
        user = Patient.query.get(user_id)
    elif role == 'admin':
        user = Admin.query.get(user_id)
    else:
        return jsonify({'success': False, 'error': '未知角色'}), 400

    if not user or not user.check_password(old_pwd):
        return jsonify({'success': False, 'error': '旧密码错误'}), 401

    user.set_password(new_pwd)
    db.session.commit()
    return jsonify({'success': True})


def init_admin():
    """初始化默认管理员账号"""
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123456')
        db.session.add(admin)
        db.session.commit()
        print('✅ 默认管理员已创建：admin / admin123456')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_admin()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

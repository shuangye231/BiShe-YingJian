from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_sock import Sock
import serial
import threading
import time
import hashlib
import random
import string
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import queue
import json

# ===================== 1. 基础配置 =====================
app = Flask(__name__)
app.secret_key = 'sensor_monitor_bishe_2026'
# MySQL连接配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/sensor_monitor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 串口配置
SERIAL_CONFIG = {
    "port": "COM3",
    "baudrate": 9600,
    "timeout": 0.1
}

# 初始化WebSocket
sock = Sock(app)
# 初始化数据库
db = SQLAlchemy(app)

# ===================== 全局变量 =====================
# 数据队列：串口→数据库解耦
data_queue = queue.Queue(maxsize=100)
# 全局最新实时数据（新增temp）
latest_sensor_data = {
    "adj": 0,
    "ntc": 0,
    "light": 0,
    "status": "Dark",
    "temp": 0.0,
    "update_time": time.strftime("%H:%M:%S")
}
# WebSocket连接池：管理所有在线的前端连接
ws_connections = []
# 连接池线程锁：避免多线程冲突
ws_lock = threading.Lock()


# ===================== 2. 数据库模型定义 =====================
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(64), nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())


class SensorData(db.Model):
    __tablename__ = 'sensor_data'
    id = db.Column(db.Integer, primary_key=True)
    adj = db.Column(db.Integer, nullable=False)
    ntc = db.Column(db.Integer, nullable=False)
    light = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    temp = db.Column(db.Float, nullable=False, default=0.0)  # 新增：温度字段
    create_time = db.Column(db.DateTime, default=db.func.now())


# ===================== 3. 工具函数 =====================
def md5_encrypt(text):
    return hashlib.md5(text.encode()).hexdigest()


def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=4))
    img = Image.new('RGB', (120, 45), color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('simhei.ttf', 28)
    except:
        font = ImageFont.load_default()
    draw.text((15, 5), captcha_text, font=font, fill=(0, 51, 102))
    for _ in range(6):
        x1, y1 = random.randint(0, 120), random.randint(0, 45)
        x2, y2 = random.randint(0, 120), random.randint(0, 45)
        draw.line((x1, y1, x2, y2), fill=(100, 150, 200), width=1)
    buf = BytesIO()
    img.save(buf, 'PNG')
    buf.seek(0)
    session['captcha'] = captcha_text.lower()
    return buf


# ===================== 核心：WebSocket数据推送函数 =====================
def push_data_to_all_clients(data):
    with ws_lock:
        json_data = json.dumps(data, ensure_ascii=False)
        for ws in ws_connections[:]:
            try:
                ws.send(json_data)
            except Exception as e:
                print(f"客户端连接失效，已移除：{e}")
                ws_connections.remove(ws)


# ===================== 串口读取线程 =====================
def serial_read_thread():
    global latest_sensor_data
    while True:
        try:
            try:
                ser = serial.Serial(**SERIAL_CONFIG)
                ser.flushInput()
                print(f"串口{SERIAL_CONFIG['port']}打开成功，开始接收数据...")
            except Exception as e:
                print(f"串口打开失败：{e}，5秒后重试...")
                time.sleep(5)
                continue

            while True:
                try:
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()
                        ser.flushInput()
                        if not line:
                            time.sleep(0.05)
                            continue
                        print(f"收到单片机数据：{line}")

                        data_parts = line.split('|')
                        parsed_data = {}
                        for part in data_parts:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                key = key.strip().lower()
                                value = value.strip()
                                parsed_data[key] = value

                        # 校验数据完整性（包含temp）
                        if all(key in parsed_data for key in ['adj', 'ntc', 'light', 'status', 'temp']):
                            latest_sensor_data = {
                                "adj": int(parsed_data['adj']),
                                "ntc": int(parsed_data['ntc']),
                                "light": int(parsed_data['light']),
                                "status": parsed_data['status'],
                                "temp": float(parsed_data['temp']),
                                "update_time": time.strftime("%H:%M:%S")
                            }
                            print(f"实时数据已更新：{latest_sensor_data}")

                            push_data_to_all_clients(latest_sensor_data)

                            try:
                                data_queue.put_nowait(latest_sensor_data.copy())
                            except queue.Full:
                                pass
                    time.sleep(0.05)
                except Exception as e:
                    print(f"串口读取异常：{e}，继续运行...")
                    time.sleep(0.05)
        except Exception as e:
            print(f"串口线程崩溃：{e}，3秒后自动重启...")
            time.sleep(3)


# ===================== 独立数据库入库线程 =====================
def db_save_thread():
    with app.app_context():
        batch_data = []
        last_save_time = time.time()
        while True:
            try:
                data = data_queue.get(timeout=1)
                batch_data.append(SensorData(
                    adj=data['adj'],
                    ntc=data['ntc'],
                    light=data['light'],
                    status=data['status'],
                    temp=data['temp']  # 新增：保存温度
                ))
                data_queue.task_done()

                if len(batch_data) >= 10 or (time.time() - last_save_time) >= 2:
                    if batch_data:
                        db.session.bulk_save_objects(batch_data)
                        db.session.commit()
                        print(f"批量入库{len(batch_data)}条历史数据")
                        batch_data = []
                        last_save_time = time.time()
            except queue.Empty:
                if batch_data and (time.time() - last_save_time) >= 2:
                    db.session.bulk_save_objects(batch_data)
                    db.session.commit()
                    print(f"超时批量入库{len(batch_data)}条历史数据")
                    batch_data = []
                    last_save_time = time.time()
                continue
            except Exception as e:
                print(f"数据库入库失败：{e}")
                db.session.rollback()
                batch_data = []


# ===================== 4. WebSocket路由 =====================
@sock.route('/ws/sensor')
def ws_sensor(ws):
    if 'user_id' not in session:
        ws.close()
        return

    with ws_lock:
        ws_connections.append(ws)
    print(f"新客户端已连接，当前在线人数：{len(ws_connections)}")

    try:
        ws.send(json.dumps(latest_sensor_data, ensure_ascii=False))
    except Exception as e:
        print(f"初始数据推送失败：{e}")

    while True:
        try:
            ws.receive()
        except:
            with ws_lock:
                if ws in ws_connections:
                    ws_connections.remove(ws)
            print(f"客户端已断开，当前在线人数：{len(ws_connections)}")
            break


# ===================== 5. 权限控制钩子 =====================
@app.before_request
def check_login():
    allow_list = ['/login', '/register', '/captcha', '/static']
    path = request.path
    if not any(path.startswith(allow_path) for allow_path in allow_list):
        if 'user_id' not in session:
            return redirect(url_for('login'))


# ===================== 6. 页面路由 =====================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        captcha = request.form.get('captcha', '').strip().lower()

        if 'captcha' not in session or captcha != session['captcha']:
            return render_template('login.html', msg='验证码错误')
        user = User.query.filter_by(username=username, password=md5_encrypt(password)).first()
        if not user:
            return render_template('login.html', msg='用户名或密码错误')

        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_pwd = request.form.get('confirm_pwd', '').strip()
        captcha = request.form.get('captcha', '').strip().lower()

        if 'captcha' not in session or captcha != session['captcha']:
            return render_template('register.html', msg='验证码错误')
        if len(username) < 3 or len(username) > 20:
            return render_template('register.html', msg='用户名长度3-20位')
        if password != confirm_pwd:
            return render_template('register.html', msg='两次密码输入不一致')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', msg='用户名已存在')

        new_user = User(username=username, password=md5_encrypt(password))
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', msg='注册成功，请登录')
    return render_template('register.html')


@app.route('/captcha')
def captcha():
    buf = generate_captcha()
    response = make_response(buf.getvalue())
    response.headers['Content-Type'] = 'image/png'
    return response


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', username=session.get('username'))


@app.route('/history')
def history():
    return render_template('history.html', username=session.get('username'))


# ===================== 7. 数据接口 =====================
@app.route('/api/realtime')
def get_realtime_data():
    return jsonify(latest_sensor_data)


@app.route('/api/history')
def get_history_data():
    limit = request.args.get('limit', 100, type=int)
    data_list = SensorData.query.order_by(SensorData.create_time.desc()).limit(limit).all()
    data_list.reverse()
    result = {
        "time": [item.create_time.strftime("%H:%M:%S") for item in data_list],
        "adj": [item.adj for item in data_list],
        "ntc": [item.ntc for item in data_list],
        "light": [item.light for item in data_list],
        "temp": [item.temp for item in data_list]  # 新增：返回温度
    }
    return jsonify(result)


# ===================== 8. 程序启动 =====================
if __name__ == '__main__':
    serial_thread = threading.Thread(target=serial_read_thread, daemon=True)
    serial_thread.start()
    db_thread = threading.Thread(target=db_save_thread, daemon=True)
    db_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
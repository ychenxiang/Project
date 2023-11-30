from flask import Flask, render_template, url_for, request, session, redirect, Response, flash
import json
import pymongo
from functools import wraps
from user.models import User
from flask_wtf.csrf import CSRFProtect
from camera import VideoCamera
import cv2
import os, sys
import numpy as np
import time
from webcam2 import FaceRecognition
from membercam import FaceRecognition_member
import tkinter as tk
from datetime import datetime
import uuid
from gridfs import GridFS



app = Flask(__name__)
app.secret_key = b'kushfuii7w4y7ry47ihwiheihf8774sdf4'

myclient = pymongo.MongoClient("mongodb+srv://team17:TqZI3KaT56q6xwYZ@team17.ufycbtt.mongodb.net/")


mydb = myclient.face
fs = GridFS(mydb, collection="faces")

video_stream = VideoCamera()

# 全局变量用于存储已拍摄的照片
captured_photo = None

global_name = None

current_datetime = datetime.now()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/')

    return wrap

def gen(camera):
    global captured_photo  # 声明全局变量
    while True:
        frame = camera.get_frame()
        if frame:
            if captured_photo:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + captured_photo + b'\r\n\r\n')
            else:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# routes
from user import routes

@app.route('/')
def home():
    user_json = session.get('user')
    if user_json:
        user = json.loads(user_json)
        user_data = json.loads(user_json)
        user_email = user_data['email']

        recent_event = list(mydb.events.find({'time': {'$gte': current_datetime}}, {'_id': 1, 'title': 1, 'time': 1}).sort("time", 1).limit(6))
        recent_sale = list(mydb.events.find({'time': {'$gte': current_datetime}}, {'_id': 1, 'title': 1, 'ticket_time': 1}).sort("ticket_time", 1).limit(6))

        return render_template('home.html',
                               user_email=user_email,
                               recent_event=recent_event,
                               recent_sale=recent_sale)
    else:
        recent_event = list(
            mydb.events.find({'time': {'$gte': current_datetime}}, {'_id': 1, 'title': 1, 'time': 1}).sort("time",
                                                                                                           1).limit(6))
        recent_sale = list(
            mydb.events.find({'time': {'$gte': current_datetime}}, {'_id': 1, 'title': 1, 'ticket_time': 1}).sort(
                "ticket_time", 1).limit(6))

        return render_template('home.html',
                               recent_event=recent_event,
                               recent_sale=recent_sale)



@app.route('/user/register')
def user_signup():
    return render_template('register.html')


@app.route('/user/login', methods=['GET','POST'])
def user_login():

    return render_template('login.html')


@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/user/update_user')
@login_required
def edit():
    user_json = session.get('user')
    if user_json:
        user = json.loads(user_json)
        return render_template('update_user.html', user=user)  # Pass the user variable to the template
    else:
        return redirect('/login')


#拍照
@app.route('/cam')
def cam():
    return render_template('cam.html', taken_photo=captured_photo)

@app.route('/video_feed')
def video_feed():
    return Response(gen(video_stream), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_photo', methods=['POST'])
def take_photo():
    global captured_photo  # 声明全局变量
    frame = video_stream.get_frame()

    if frame:
        # 使用 OpenCV 解码 JPEG 图像为 NumPy 数组
        nparr = np.frombuffer(frame, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 使用当前时间戳作为文件名
        timestamp = int(time.time())

        # 将照片数据存储在 captured_photo 中
        captured_photo = cv2.imencode('.jpg', image)[1].tobytes()

    return render_template('cam.html', taken_photo=captured_photo)

@app.route('/save_photo', methods=['POST'])
def save_photo():
    global captured_photo  # 声明全局变量
    if captured_photo:

        # 使用者名字當檔名
        user_json = session.get('user')  # Get user JSON from session
        user_data = json.loads(user_json)  # Parse JSON to dictionary
        user_name = user_data['name']

        try:
            photo_id = fs.put(captured_photo, filename=f"{user_name}")
            print(f"Photo saved with ID: {photo_id}")
        except Exception as e:
            print(f"Error saving photo: {str(e)}")
        return redirect(url_for('memberprofile'))

@app.route('/retake_photo', methods=['POST'])
def retake_photo():
    global captured_photo  # 声明全局变量
    captured_photo = None  # 重置 captured_photo 为 None
    return render_template('cam.html', taken_photo=captured_photo)


#人臉辨識(入場辨識)
@app.route('/cam2')
def cam2():
    return render_template('cam2.html')

def generate_frames():
    fr = FaceRecognition()
    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        sys.exit('video source not found...')

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame = fr.run_recognition(frame)

        if frame is not None:  # 檢查 frame 是否為有效的圖像
            _, buffer = cv2.imencode('.jpg', frame)
            if buffer is not None:  # 檢查 buffer 是否為有效的編碼
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                print("Error encoding frame")
        else:
            print("No frame captured")

            # 檢查是否需要退出捕獲視頻
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

# 人臉辨識(驗證使用者)
@app.route('/cam3')
def cam3():
    return render_template('cam3.html')


# 人臉辨識(驗證使用者)
@app.route('/set_name')
def set_name():
    # 將名字設定為 session 的值
    # name = session.get('name')
    user_json = session.get('user')  # Get user JSON from session
    user_data = json.loads(user_json)  # Parse JSON to dictionary
    name = user_data['name']
    print("這裡是setname")

    # 同時也設定全域變數 global_name
    global global_name
    global_name = name

    return 'Name set successfully'


@app.route('/video_feed2')
def video_feed2():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/memberprofile')
@login_required
def memberprofile():
    user_json = session.get('user')
    if user_json:
        user = json.loads(user_json)
        user_data = json.loads(user_json)
        user_email = user_data['email']
        return render_template('memberprofile.html', user_email=user_email)
    else:
        print("user_json is NOT a thing")
        return redirect('/user/login')


@app.route('/user/showphoto')
@login_required
def showphoto():
    return render_template('showphoto.html')


@app.route('/admin')
@login_required
def admin():
    print("this is the app.py, going to admin.html")
    return render_template('admin.html')


@app.route('/test_error')
def test_admin_error():
    return render_template('test_error.html')

@app.route("/add_event")
def admin_add_event():
    return render_template('add_event.html')



if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5000)
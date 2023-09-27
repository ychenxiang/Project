from flask import Flask, render_template, Response, session
from camera import VideoCamera
import cv2
import os
import numpy as np
import time

app = Flask(__name__)
app.secret_key = b'kushfuii7w4y7ry47ihwiheihf8774sdf4'

video_stream = VideoCamera()

# 全局变量用于存储已拍摄的照片
captured_photo = None

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

@app.route('/')
def index():
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
        user_name = session.get('user_name')

        # 指定保存到 "faces" 子文件夹的路径
        output_folder = 'faces'

        # 确保目标文件夹存在，如果不存在则创建它
        os.makedirs(output_folder, exist_ok=True)

        # 创建完整的文件路径，将照片保存到 "faces" 子文件夹中
        photo_filename = os.path.join(output_folder, f'{user_name}.jpg')

        # 写入照片数据到文件
        with open(photo_filename, 'wb') as photo_file:
            photo_file.write(captured_photo)

    return render_template('cam.html', taken_photo=captured_photo)

@app.route('/retake_photo', methods=['POST'])
def retake_photo():
    global captured_photo  # 声明全局变量
    captured_photo = None  # 重置 captured_photo 为 None
    return render_template('cam.html', taken_photo=captured_photo)

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True, port=5000)

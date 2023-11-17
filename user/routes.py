from flask import Flask, session, Response, redirect,render_template, url_for
from app import app
from user.models import User, Event
import cv2
from membercam import FaceRecognition_member
from tkinter import messagebox
import json
import webbrowser


global_name = None
result = 0


@app.route('/user/signup', methods=['POST'])
def signup():
    return User().signup()

@app.route('/user/signout')
def signout():
    return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
    return User().login()
'''
@app.route('/user/update_user', methods=['POST'])
def update_user():
    return User().update_user()
'''
@app.route('/user/update_user', methods=['POST'])
def update_user_route():
    user_obj = User()
    return user_obj.update_user()

@app.route("/memberlist", methods = ['GET'])
def get_all_member():
    return User().get_all_member()


@app.route("/delete_member/<string:email>", methods = ['GET'])
def delete_member(email):
    #print("passed routes.py, reaching for User.get_all_member()")
    return User().delete_member(email)

@app.route("/get_member/<string:email>", methods = ['GET'])
def get_member(email):
    return User().get_member(email)

### testing
@app.route("/test", methods = ['GET'])
def test_get_all_member():
    return User().test_get_all_member()
### end testing


@app.route("/eventlist", methods = ['GET'])
def get_all_event():
    return Event().get_all_event()

@app.route('/event/<event_id>/image')
def get_event_image(event_id):
    return Event().get_event_image(event_id)

@app.route("/add_event", methods = ['POST'])
def add_event():
    return Event().add_event()


@app.route("/delete_event/<string:title>", methods = ['GET'])
def delete_event(title):
    print("routes: delete event")
    return Event().delete_event(title)


@app.route("/get_event/<event_id>", methods = ['GET'])
def get_event(event_id):
    return Event().get_event(event_id)


@app.route('/ad_event/<event_id>')
def ad_event_details(event_id):
    return Event().ad_event_details(event_id)


@app.route("/modify_event/<event_id>", methods = ['GET', 'POST'])
def modify_event(event_id):
    return Event().modify_event(event_id)

@app.route('/membercam')
def membercam():
    user_json = session.get('user')  # Get user JSON from session
    user_data = json.loads(user_json)  # Parse JSON to dictionary
    name = user_data['name']
    print("這裡是setname")

    # 同時也設定全域變數 global_name
    global global_name
    global_name = name

    return render_template('membercam.html')

@app.route('/video_feed3')
def video_feed3():
    return Response(generate_frames_session(session), mimetype='multipart/x-mixed-replace; boundary=frame')

def generate_frames_session(session):
    fr = FaceRecognition_member()
    video_capture = cv2.VideoCapture(0)

    correct = 0
    fail = 0

    if not video_capture.isOpened():
        return 'Video source not found'
    count = 0

    while count < 5:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame, recognized_name = fr.run_recognition(frame)
        recognized_name = recognized_name.split('(', 1)

        # 從 session 中獲取名字
        global session_name
        session_name = global_name
        print(session_name)
        print(recognized_name)
        # 比對辨識出來的名字和 session 中的名字是否一致
        if recognized_name[0] == session_name:
            print("辨識結果和 session 中的名字一致")
            #show_success_popup(session_name)
            correct += 1
            #return redirect(url_for('recognition_correct'))
            #flash("辨識結果和 session 中的名字一致", "success")
        else:
            print("辨識結果和 session 中的名字不一致")
            fail += 1
            #return redirect(url_for('recognition_fail.html'))
            #flash("辨識結果和 session 中的名字不一致", "error")

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        count += 1

    print(correct, fail)
    global result
    result = correct / (correct + fail)
    video_capture.release()


@app.route('/recognition_result')
def recognition_result():
    global result
    if result >= 0.75:
        print(result)
        #show_success_popup(session_name)
        return render_template('recognition_correct.html')
    elif result <0.75:
        print(result)
        #show_fail_popup(session_name)
        return render_template('recognition_fail.html')

@app.route('/recognition_correct')
def recognition_correct():
    print('成功進結果網頁')
    print(result)
    return render_template('recognition_correct.html')

@app.route('/recognition_fail')
def recognition_fail():
    print('成功進判斷式')
    print(result)
    return render_template('recognition_fail.html')


def show_success_popup(name):
    message = f"{name} 成功驗證為本人"
    messagebox.showinfo('Recognition Success', message)  # 訊息內容
    webbrowser.open('http://127.0.0.1:5000/recognition_correct')

def show_fail_popup(name):
    message = f"{name} 驗證失敗"
    messagebox.showwarning(title='Recognition Fail',  # 視窗標題
                        message=message)  # 訊息內容
    webbrowser.open('http://127.0.0.1:5000/recognition_fail')

@app.route('/search', methods=['POST'])
def search():
    return User().search()

@app.route('/event/<event_id>')
def event_details(event_id):
    return User().event_details(event_id)

@app.route("/all_event", methods = ['GET'])
def all_event():
    return User.all_event()
    #return render_template('all_event.html')


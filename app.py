from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 세션 암호화에 사용됨
# MongoDB 연결
uri = "mongodb://id:pw@3.39.11.17/"
client = MongoClient(uri, 27017)
db = client["user_db"]
users_collection = db["users"]
profile_collection = db['profiles']
bcrypt = Bcrypt(app)
@app.route('/')
def home():
    if 'username' in session:
        return f"안녕하세요, {session['username']}님!<a href='/logout'>로그아웃</a><br><input type='text' name='UserInfo' placeholder='자기소개' required><br>"
    return "로그인되지 않았습니다. <a href='/login'>로그인</a>"
@app.route('/sign', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_img = request.form['UserImg']
        user_id = request.form['UserId']
        user_password = request.form['UserPassword']
        user_re_password = request.form['UserRePassword']
        user_name = request.form['UserName']
        user_school = request.form['UserSchool']
        user_email = request.form['UserEmail']
        user_info = request.form.get('UserInfo', '')
        profile_content = request.form.get('profile_Content', '')
        # 필수 입력값 확인
        if not all([user_id, user_password, user_re_password, user_name, user_email]):
            return "모든 항목을 입력해주세요."
        # 아이디 중복 확인
        if users_collection.find_one({"UserId": user_id}):
            return "이미 존재하는 아이디입니다."
        # 비밀번호 확인
        if user_password != user_re_password:
            return "비밀번호가 일치하지 않습니다."
        # 비밀번호 해싱
        hashed_password = bcrypt.generate_password_hash(user_password).decode('utf-8')
        # DB 저장
        users_collection.insert_one({
            "UserImg": user_img,
            "UserId": user_id,
            "Password": hashed_password,
            "UserName": user_name,
            "UserSchool": user_school,
            "UserEmail": user_email,
            "UserInfo": user_info
        })
        profile_collection.insert_one({
            "UserImg": user_img,
            "UserId": user_id,
            "UserName": user_name,
            "UserSchool": user_school,
            "UserEmail": user_email,
            "UserInfo": user_info,
            "profile_Content": profile_content
        })
        # 세션 저장
        session['user_id'] = user_id
        session['username'] = user_name
        return redirect(url_for('home'))
    return render_template('signup.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['username']
        user_password = request.form['password']
        # 사용자 조회
        user = users_collection.find_one({"UserId": user_id})
        if user and bcrypt.check_password_hash(user['Password'], user_password):
            session['user_id'] = user_id
            session['username'] = user['UserName']
            return redirect(url_for('home'))
        return "로그인 실패! 아이디나 비밀번호를 확인하세요."
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('home'))
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = users_collection.find_one({"UserId": user_id})
    profile = profile_collection.find_one({"UserId": user_id})
    if request.method == 'POST':
        main_titles = request.form.getlist('main_title[]')
        sub_contents = request.form.getlist('sub_content[]')
        profile_content = []
        for title, content in zip(main_titles, sub_contents):
            if title.strip() or content.strip():
                profile_content.append({
                    "main_title": title.strip(),
                    "sub_content": content.strip()
                })
        profile_collection.update_one(
            {"UserId": user_id},
            {"$set": {"profile_Content": profile_content}}
        )
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user, profile=profile)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
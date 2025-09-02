from flask import Blueprint, request, render_template, redirect, url_for, jsonify, make_response
from extensions import users_collection, bcrypt
import util, jwt

auth_api_bp = Blueprint("auth_api", __name__, url_prefix="/auth/api")

@auth_api_bp.route("/sign", methods=["POST"])
def api_signup():
    user_id = request.form.get("UserId", "").strip()
    user_password = request.form.get("UserPassword", "")
    user_re_password = request.form.get("UserRePassword", "")
    user_name = request.form.get("UserName", "").strip()
    user_email = request.form.get("UserEmail", "").strip().lower()

    if not all([user_id, user_password, user_re_password, user_name, user_email]):
        return render_template("signup.html", error_msg="모든 항목을 입력해주세요.")
    if user_password != user_re_password:
        return render_template("signup.html", error_msg="비밀번호가 일치하지 않습니다.")
    if users_collection.find_one({"UserId": user_id}):
        return render_template("signup.html", error_msg="이미 존재하는 아이디입니다.")

    hashed = bcrypt.generate_password_hash(user_password).decode("utf-8")
    users_collection.insert_one({
        "UserId": user_id,
        "PasswordHash": hashed,
        "UserName": user_name,
        "UserEmail": user_email,
        "CreatedAt": util.now_utc()
    })
    return redirect(url_for("auth_views.view_login"))

@auth_api_bp.route("/login", methods=["POST"])
def api_login():
    user_id = request.form.get("UserId", "").strip()
    user_password = request.form.get("UserPassword", "")

    user = users_collection.find_one({"UserId": user_id})
    stored = (user or {}).get("PasswordHash")
    if not stored or not bcrypt.check_password_hash(stored, user_password):
        return render_template("login.html", error_msg="잘못된 아이디 혹은 비밀번호입니다.")

    access = util.create_access_token(user)
    resp = make_response(redirect(url_for("logined")))
    return util.set_access_cookie(resp, access)

@auth_api_bp.route("/logout")
def api_logout():
    resp = make_response(redirect(url_for("home")))
    return util.clear_access_cookie(resp)

@auth_api_bp.route("/auth", methods=["GET"])
def api_auth():
    token = request.cookies.get("access_token")
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    try:
        decoded = util.decode_token(token)
        return jsonify({"UserId": decoded.get("sub"), "UserName": decoded.get("name")})
    except jwt.ExpiredSignatureError:
        return jsonify({"msg": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"msg": "Invalid token"}), 401
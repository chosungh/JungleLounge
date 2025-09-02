from flask import Blueprint, render_template

auth_views_bp = Blueprint("auth_views", __name__, url_prefix="/auth/view")

@auth_views_bp.route("/signup", methods=["GET"])
def view_signup():
    return render_template("signup.html")

@auth_views_bp.route("/login", methods=["GET"])
def view_login():
    return render_template("login.html", error_msg="")
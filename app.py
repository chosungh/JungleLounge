from flask import Flask, render_template, request
from auth import auth_views_bp, auth_api_bp   # auth/__init__.py에서 export

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-flask-secret"  # 환경변수로 교체 권장
def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "replace-flask-secret"
    app.register_blueprint(auth_views_bp)
    app.register_blueprint(auth_api_bp)

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/logined")
    def logined():
        return render_template("logined_index.html")

    return app
if __name__ == "__main__":
    app = create_app()
    # 개발 시 debug=True, 배포 시 False
    app.run(host="0.0.0.0", port=5005, debug=True)
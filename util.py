import os, jwt
from datetime import datetime, timedelta, timezone
from flask import make_response

JWT_SECRET = os.getenv("JWT_SECRET", "thisiskeythatishard")
JWT_ALG = "HS256"
ACCESS_EXPIRE_MIN = 15
COOKIE_SECURE = False
COOKIE_SAMESITE = "Lax"

def now_utc():
    return datetime.now(timezone.utc)

def create_access_token(user_doc: dict) -> str:
    payload = {
        "sub": user_doc["UserId"],
        "name": user_doc["UserName"],
        "iat": int(now_utc().timestamp()),
        "exp": int((now_utc() + timedelta(minutes=ACCESS_EXPIRE_MIN)).timestamp()),
        "typ": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])

def set_access_cookie(resp, token: str):
    resp.set_cookie(
        "access_token", token,
        httponly=True, secure=COOKIE_SECURE, samesite=COOKIE_SAMESITE,
        max_age=ACCESS_EXPIRE_MIN * 60, path="/"
    )
    return resp

def clear_access_cookie(resp):
    resp.delete_cookie("access_token", path="/")
    return resp

def redirect_with_cookie(token, location_endpoint, url_for):
    resp = make_response(url_for(location_endpoint))  # 사용 안 해도 가능 예시
    return set_access_cookie(resp, token)
"""TOPIC 2 - Authentication, profile, roles"""
from flask import Blueprint
from ..core import *
from ..services.inventory import *
from ..services.ai_engine import *

bp = Blueprint("auth", __name__)


@bp.post("/api/register")
def register():
    d = request.json or {}
    if not d.get("email") or len(d.get("password", "")) < 6 or not d.get("name"):
        return jsonify(error="Name, email and a password of 6+ characters are required"), 400
    if q("select 1 from users where email=?", (d["email"].lower(),)):
        return jsonify(error="Email already registered"), 400
    uid = ex("insert into users(name,email,password,role,department) values(?,?,?,?,?)",
             (d["name"], d["email"].lower(), generate_password_hash(d["password"]), "Faculty Member", d.get("department", "")))
    session["uid"] = uid
    return jsonify(ok=True)


@bp.post("/api/login")
def login():
    d = request.json or {}
    u = q("select * from users where email=?", ((d.get("email") or "").lower(),), one=True)
    if not u or not check_password_hash(u["password"], d.get("password", "")):
        return jsonify(error="Invalid email or password"), 401
    session.clear(); session["uid"] = u["id"]; session.permanent = True
    return jsonify(ok=True)


@bp.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@bp.get("/api/me")
@need()
def me():
    u = dict(g.user); u.pop("password"); u.pop("reset_token")
    return jsonify(u)


@bp.put("/api/me")
@need()
def update_me():
    d = request.json or {}
    ex("update users set name=?, department=? where id=?", (d.get("name", g.user["name"]), d.get("department", ""), g.user["id"]))
    if d.get("password"):
        if len(d["password"]) < 6:
            return jsonify(error="Password too short"), 400
        ex("update users set password=? where id=?", (generate_password_hash(d["password"]), g.user["id"]))
    return jsonify(ok=True)


@bp.post("/api/forgot")
def forgot():
    u = q("select id from users where email=?", ((request.json or {}).get("email", "").lower(),), one=True)
    if u:
        t = secrets.token_urlsafe(8)
        ex("update users set reset_token=? where id=?", (t, u["id"]))
        print(f"[PASSWORD RESET] token for user {u['id']}: {t}  (wire this to email in production)")
    return jsonify(ok=True, message="If the email exists, a reset token was sent (see server console in demo mode).")


@bp.post("/api/reset")
def reset():
    d = request.json or {}
    u = q("select id from users where reset_token=? and reset_token!=''", (d.get("token", ""),), one=True)
    if not u or len(d.get("password", "")) < 6:
        return jsonify(error="Invalid token or weak password"), 400
    ex("update users set password=?, reset_token='' where id=?", (generate_password_hash(d["password"]), u["id"]))
    return jsonify(ok=True)


@bp.get("/api/users")
@need(*ADMIN)
def users():
    return jsonify(q("select id,name,email,role,department from users"))


@bp.put("/api/users/<int:uid>/role")
@need(*ADMIN)
def set_role(uid):
    r = (request.json or {}).get("role")
    if r not in ROLES:
        return jsonify(error="Bad role"), 400
    ex("update users set role=? where id=?", (r, uid))
    return jsonify(ok=True)

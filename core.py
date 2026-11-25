"""TOPIC 1 - Core: database helpers, constants, login/role guard."""
import sqlite3, os, io, re, random, secrets
from datetime import date, timedelta
from functools import wraps
from flask import g, request, jsonify, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
DB = os.environ.get("EQUIPAI_DB", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inventory.db"))
ROLES = ["Super Admin", "College Administrator", "Department Head", "Lab Assistant", "Faculty Member"]
MANAGE, APPROVE, ADMIN = ROLES[:4], ROLES[:3], ROLES[:2]
F = ["name", "category", "brand", "model_no", "serial_no", "department", "lab", "purchase_date",
     "purchase_cost", "warranty_expiry", "quantity", "cond", "status", "image", "description"]
today = lambda: date.today().isoformat()


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


def close(_):
    d = g.pop("db", None)
    if d:
        d.close()


def q(sql, a=(), one=False):
    r = [dict(x) for x in db().execute(sql, a).fetchall()]
    return (r[0] if r else None) if one else r


def ex(sql, a=()):
    c = db().execute(sql, a)
    db().commit()
    return c.lastrowid


def need(*roles):
    def deco(f):
        @wraps(f)
        def w(*a, **k):
            u = q("select * from users where id=?", (session.get("uid"),), one=True)
            if not u:
                return jsonify(error="Please log in"), 401
            if roles and u["role"] not in roles:
                return jsonify(error="Not permitted for your role"), 403
            g.user = u
            return f(*a, **k)
        return w
    return deco

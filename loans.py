"""TOPIC 5 - Issue and return workflow"""
from flask import Blueprint
from ..core import *
from ..services.inventory import *
from ..services.ai_engine import *

bp = Blueprint("loans", __name__)


@bp.get("/api/requests")
@need()
def req_list():
    sql = "select r.*, e.name equip, u.name requester from requests r join equipment e on e.id=r.equip_id join users u on u.id=r.user_id"
    if g.user["role"] == "Faculty Member":
        return jsonify(q(sql + " where r.user_id=? order by r.id desc", (g.user["id"],)))
    return jsonify(q(sql + " order by r.id desc"))


@bp.post("/api/requests")
@need()
def req_add():
    d = request.json or {}
    e = next((x for x in equipment_rows() if x["id"] == int(d.get("equip_id", 0))), None)
    n = int(d.get("qty", 1))
    if not e or n < 1 or n > e["available"]:
        return jsonify(error="Invalid quantity or equipment not available"), 400
    ex("insert into requests(equip_id,user_id,qty,status,req_date,purpose) values(?,?,?,?,?,?)",
       (e["id"], g.user["id"], n, "Pending", today(), d.get("purpose", "")))
    return jsonify(ok=True)


@bp.post("/api/requests/<int:i>/<act>")
@need(*MANAGE)
def req_act(i, act):
    r = q("select * from requests where id=?", (i,), one=True)
    if not r: return jsonify(error="Not found"), 404
    flow = {"approve": ("Pending", "Approved"), "reject": ("Pending", "Rejected"),
            "issue": ("Approved", "Issued"), "return": ("Issued", "Returned")}
    if act not in flow or r["status"] != flow[act][0]:
        return jsonify(error=f"Cannot {act} a {r['status']} request"), 400
    if act in ("approve", "reject") and g.user["role"] not in APPROVE:
        return jsonify(error="Only admins/heads can approve"), 403
    if act == "issue":
        days = int((request.json or {}).get("days", 7))
        ex("update requests set status='Issued', issue_date=?, due_date=? where id=?", (today(), (date.today() + timedelta(days=days)).isoformat(), i))
    elif act == "return":
        ex("update requests set status='Returned', return_date=? where id=?", (today(), i))
    else:
        ex("update requests set status=? where id=?", (flow[act][1], i))
    return jsonify(ok=True)

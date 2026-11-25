"""TOPIC 3 - Dashboard data"""
from flask import Blueprint
from ..core import *
from ..services.inventory import *
from ..services.ai_engine import *

bp = Blueprint("dashboard", __name__)


@bp.get("/api/dashboard")
@need()
def dashboard():
    rows = equipment_rows()
    dep, cond = {}, {}
    for e in rows:
        dep[e["department"]] = dep.get(e["department"], 0) + e["quantity"]
        cond[e["cond"]] = cond.get(e["cond"], 0) + e["quantity"]
    top = q("select e.name, count(*) n from requests r join equipment e on e.id=r.equip_id group by e.id order by n desc limit 5")
    recent = q("select r.status, r.req_date, e.name, u.name who from requests r join equipment e on e.id=r.equip_id join users u on u.id=r.user_id order by r.id desc limit 8")
    return jsonify(stats=stats(), departments=dep, conditions=cond, usage=monthly_usage(), top=top, recent=recent,
                   low=[e for e in rows if e["available"] <= 2][:6])

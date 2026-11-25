"""TOPIC 6/7 - AI endpoints and EquipAI chatbot"""
from flask import Blueprint
from ..core import *
from ..services.inventory import *
from ..services.ai_engine import *

bp = Blueprint("ai", __name__)


@bp.get("/api/ai/demand")
@need()
def ai_demand(): return jsonify(demand_report())


@bp.get("/api/ai/maintenance")
@need()
def ai_maint(): return jsonify(maintenance_report())


@bp.get("/api/ai/alerts")
@need()
def ai_alerts(): return jsonify(alerts_report())


@bp.get("/api/ai/recommend")
@need()
def ai_rec(): return jsonify(recommend_report())


@bp.post("/api/ai/chat")
@need()
def chat():
    m = ((request.json or {}).get("message") or "").lower().strip()
    rows, s = equipment_rows(), stats()
    if "summary" in m or "overview" in m:
        a = (f"Inventory summary: {s['total']} items in total, {s['available']} available, {s['issued']} issued, "
             f"{s['maintenance']} under maintenance, {s['damaged']} damaged, {s['pending']} pending requests.")
    elif "damaged" in m:
        d = [e for e in rows if e["cond"] == "Damaged"]
        a = "Damaged equipment: " + "; ".join(f"{e['name']} in {e['lab']} ({e['department']})" for e in d) if d else "No damaged equipment recorded."
    elif "issued" in m:
        r = q("select e.name, r.qty, u.name who, r.due_date from requests r join equipment e on e.id=r.equip_id join users u on u.id=r.user_id where r.status='Issued'")
        a = "Currently issued: " + "; ".join(f"{x['name']} x{x['qty']} to {x['who']} (due {x['due_date']})" for x in r) if r else "Nothing is currently issued."
    elif "maintenance" in m or "repair" in m:
        r = [x for x in maintenance_report() if x["level"] != "Low"][:6]
        a = "Needs attention: " + "; ".join(f"{x['name']} ({x['level']} risk, {x['score']}/100)" for x in r) if r else "No equipment needs maintenance."
    elif "usage" in m or "department" in m and ("highest" in m or "most" in m):
        r = q("select e.department d, count(*) n from requests r join equipment e on e.id=r.equip_id group by d order by n desc limit 3")
        a = "Highest usage by department: " + ", ".join(f"{x['d']} ({x['n']} requests)" for x in r)
    elif "overdue" in m:
        a = "; ".join(x["text"] for x in alerts_report() if x["title"] == "Overdue") or "No overdue equipment."
    elif "warranty" in m:
        a = "; ".join(x["text"] for x in alerts_report() if "Warranty" in x["title"]) or "No warranties expiring in 60 days."
    elif "recommend" in m or "buy" in m or "purchase" in m:
        a = "Suggested purchases: " + "; ".join(f"{x['name']} (+{x['suggested_qty']}) - {x['reasons']}" for x in recommend_report()[:4])
    else:
        mt = re.search(r"(?:how many|count|available|is there|are there)\s+([a-z0-9 ]+?)(?:s)?\s*(?:available|are|do|in|\?|$)", m)
        words = [w.rstrip("s") for w in re.findall(r"[a-z0-9]+", m) if w not in ("how", "many", "are", "available", "is", "there", "the", "do", "we", "have", "show", "me", "what", "in", "of", "any")]
        hit = [e for e in rows if any(w and (w in e["name"].lower() or w in e["category"].lower()) for w in words)] if words else []
        if hit:
            a = "; ".join(f"{e['name']}: {e['available']} available of {e['quantity']} ({e['lab']})" for e in hit)
        else:
            a = "I can answer questions about availability, damaged, issued, maintenance, usage, overdue, warranty, purchases, or ask for a summary."
    return jsonify(reply=a)

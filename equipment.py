"""TOPIC 4 - Equipment CRUD, search/sort, Excel/PDF export"""
from flask import Blueprint
from ..core import *
from ..services.inventory import *
from ..services.ai_engine import *

bp = Blueprint("equipment", __name__)


@bp.get("/api/equipment")
@need()
def eq_list():
    rows = equipment_rows()
    s, dep, cat = request.args.get("q", "").lower(), request.args.get("dept", ""), request.args.get("cat", "")
    rows = [e for e in rows if (not s or s in (e["name"] + e["brand"] + e["serial_no"] + e["lab"] + e["code"]).lower())
            and (not dep or e["department"] == dep) and (not cat or e["category"] == cat)]
    key = request.args.get("sort", "name")
    rows.sort(key=lambda e: (e.get(key) is None, e.get(key) or 0), reverse=request.args.get("desc") == "1")
    return jsonify(rows)


def clean(d):
    v = {k: d.get(k, "") for k in F}
    v["quantity"] = int(v["quantity"] or 1)
    v["purchase_cost"] = float(v["purchase_cost"] or 0)
    v["cond"] = v["cond"] or "Good"; v["status"] = v["status"] or "Available"
    return v


@bp.post("/api/equipment")
@need(*MANAGE)
def eq_add():
    v = clean(request.json or {})
    if not v["name"]:
        return jsonify(error="Name required"), 400
    i = ex(f"insert into equipment({','.join(F)}) values({','.join('?'*len(F))})", [v[k] for k in F])
    return jsonify(id=i)


@bp.put("/api/equipment/<int:i>")
@need(*MANAGE)
def eq_edit(i):
    v = clean(request.json or {})
    ex(f"update equipment set {','.join(k+'=?' for k in F)} where id=?", [v[k] for k in F] + [i])
    return jsonify(ok=True)


@bp.delete("/api/equipment/<int:i>")
@need(*APPROVE)
def eq_del(i):
    ex("delete from equipment where id=?", (i,)); ex("delete from requests where equip_id=?", (i,))
    return jsonify(ok=True)


@bp.get("/api/export/<kind>")
@need()
def export(kind):
    rows = equipment_rows()
    cols = ["code", "name", "category", "brand", "department", "lab", "quantity", "available", "cond", "status", "purchase_cost"]
    buf = io.BytesIO()
    if kind == "excel":
        from openpyxl import Workbook
        wb = Workbook(); ws = wb.active; ws.append([c.upper() for c in cols])
        for r in rows: ws.append([r[c] for c in cols])
        wb.save(buf); buf.seek(0)
        return send_file(buf, as_attachment=True, download_name="equipment.xlsx")
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors
    t = Table([[c.upper() for c in cols]] + [[str(r[c]) for c in cols] for r in rows], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#14213D")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), .25, colors.grey)]))
    SimpleDocTemplate(buf, pagesize=landscape(A4)).build([t]); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name="equipment.pdf")

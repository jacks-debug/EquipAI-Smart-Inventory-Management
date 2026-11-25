"""TOPIC 6 - AI engine: demand forecast, maintenance risk, alerts, recommendations."""
from ..core import *
from .inventory import *


def forecast(series):
    n = len(series)
    xs = list(range(n)); mx = sum(xs) / n; my = sum(series) / n
    den = sum((x - mx) ** 2 for x in xs) or 1
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, series)) / den
    return max(0, round(my + slope * (n - mx), 1)), round(slope, 2)


def risk(e, usage, mcount):
    age = (date.today() - date.fromisoformat(e["purchase_date"])).days / 365 if e["purchase_date"] else 0
    s = age * 8 + {"Excellent": 0, "Good": 5, "Fair": 25, "Poor": 45, "Damaged": 70}.get(e["cond"], 10) + usage * 2.5 + mcount * 6
    s = min(100, round(s))
    return s, "High" if s >= 60 else "Medium" if s >= 35 else "Low"


def maintenance_report():
    use = {r["equip_id"]: r["n"] for r in q("select equip_id,count(*) n from requests group by equip_id")}
    mc = {r["equip_id"]: r["n"] for r in q("select equip_id,count(*) n from maintenance group by equip_id")}
    out = []
    for e in equipment_rows():
        s, lvl = risk(e, use.get(e["id"], 0), mc.get(e["id"], 0))
        tip = {"High": "Schedule inspection within 7 days", "Medium": "Plan preventive service this month", "Low": "Routine checks only"}[lvl]
        out.append(dict(id=e["id"], code=e["code"], name=e["name"], lab=e["lab"], score=s, level=lvl, advice=tip, cond=e["cond"]))
    return sorted(out, key=lambda x: -x["score"])


def demand_report():
    out = []
    avail = {}
    for e in equipment_rows():
        avail[e["department"]] = avail.get(e["department"], 0) + e["available"]
    for d in q("select distinct department from equipment"):
        dep = d["department"]
        ser = monthly_usage("and equip_id in (select id from equipment where department=?)", (dep,))
        pred, slope = forecast([n for _, n in ser])
        out.append(dict(department=dep, history=[n for _, n in ser], months=[m for m, _ in ser], predicted=pred,
                        trend="rising" if slope > .2 else "falling" if slope < -.2 else "stable",
                        available=avail.get(dep, 0), needs_more=pred * 2 > avail.get(dep, 0)))
    return out


def alerts_report():
    al, rows = [], equipment_rows()
    for e in rows:
        if e["available"] <= 2 and e["status"] == "Available":
            al.append(("warning", "Low stock", f"{e['name']} ({e['lab']}): only {e['available']} available"))
        if e["warranty_expiry"]:
            days = (date.fromisoformat(e["warranty_expiry"]) - date.today()).days
            if 0 <= days <= 60:
                al.append(("warning", "Warranty expiring", f"{e['name']} warranty ends in {days} days"))
    for r in maintenance_report():
        if r["level"] == "High":
            al.append(("danger", "Maintenance due", f"{r['name']} risk {r['score']}/100: {r['advice']}"))
    for r in q("select r.*, e.name from requests r join equipment e on e.id=r.equip_id where r.status='Issued' and r.due_date<?", (today(),)):
        al.append(("danger", "Overdue", f"{r['name']} x{r['qty']} was due {r['due_date']}"))
    m = monthly_usage()
    base = sum(n for _, n in m[:-1]) / 5 or 1
    if m[-1][1] > base * 1.8 and m[-1][1] > 5:
        al.append(("info", "Unusual usage", f"This month's requests ({m[-1][1]}) are far above the average ({base:.1f})"))
    return [dict(level=a, title=b, text=c) for a, b, c in al]


def recommend_report():
    cost = {r["d"]: r["c"] for r in q("select e.department d, sum(m.cost) c from maintenance m join equipment e on e.id=m.equip_id group by d")}
    recs = []
    use = {r["equip_id"]: r["n"] for r in q("select equip_id,count(*) n from requests where status!='Rejected' group by equip_id")}
    for e in equipment_rows():
        u = use.get(e["id"], 0)
        util = (e["issued"] / e["quantity"]) if e["quantity"] else 0
        score = u * 2 + util * 20 + (15 if e["cond"] in ("Poor", "Damaged") else 0) + (10 if e["available"] <= 2 else 0)
        why = []
        if u > 12: why.append("high historical usage")
        if e["available"] <= 2: why.append("low availability")
        if e["cond"] in ("Poor", "Damaged"): why.append("poor condition, consider replacement")
        if cost.get(e["department"], 0) > 5000: why.append("high department maintenance spend")
        if why:
            recs.append(dict(name=e["name"], department=e["department"], score=round(score),
                             suggested_qty=max(1, round(e["quantity"] * .2)), reasons=", ".join(why)))
    return sorted(recs, key=lambda x: -x["score"])[:8]

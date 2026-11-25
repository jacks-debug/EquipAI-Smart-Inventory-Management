"""TOPIC 3/4 - Inventory calculations shared by every module."""
from ..core import *


def equipment_rows():
    issued = {r["equip_id"]: r["n"] for r in q("select equip_id, sum(qty) n from requests where status='Issued' group by equip_id")}
    rows = q("select * from equipment")
    for e in rows:
        e["code"] = "EQ-%04d" % e["id"]
        e["issued"] = issued.get(e["id"], 0)
        blocked = e["quantity"] if e["status"] != "Available" or e["cond"] == "Damaged" else 0
        e["available"] = max(0, e["quantity"] - e["issued"] - (blocked if blocked else 0))
    return rows


def monthly_usage(where="", args=()):
    rows = q(f"select strftime('%Y-%m',req_date) m, count(*) n from requests where status!='Rejected' {where} group by m", args)
    d = {r["m"]: r["n"] for r in rows}
    out, t = [], date.today().replace(day=1)
    for i in range(5, -1, -1):
        y, m = t.year, t.month - i
        while m < 1:
            m += 12; y -= 1
        k = f"{y}-{m:02d}"
        out.append((k, d.get(k, 0)))
    return out


def stats():
    rows = equipment_rows()
    tot = sum(e["quantity"] for e in rows)
    return dict(total=tot, available=sum(e["available"] for e in rows), issued=sum(e["issued"] for e in rows),
                maintenance=sum(e["quantity"] for e in rows if e["status"] == "Under Maintenance"),
                damaged=sum(e["quantity"] for e in rows if e["cond"] == "Damaged"),
                pending=q("select count(*) n from requests where status='Pending'", one=True)["n"])

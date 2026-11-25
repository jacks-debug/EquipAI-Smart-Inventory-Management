import os, sys, tempfile
os.environ["EQUIPAI_DB"] = os.path.join(tempfile.mkdtemp(), "t.db")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import create_app
c = create_app().test_client()
assert c.get("/").status_code == 200
assert c.post("/api/login", json={"email": "admin@college.edu", "password": "admin123"}).status_code == 200
for u in ["dashboard", "equipment", "requests", "users", "ai/demand", "ai/maintenance", "ai/alerts", "ai/recommend", "export/excel", "export/pdf"]:
    assert c.get("/api/" + u).status_code == 200, u
assert "available" in c.post("/api/ai/chat", json={"message": "how many computers are available"}).json["reply"]
print("ALL TESTS PASSED")

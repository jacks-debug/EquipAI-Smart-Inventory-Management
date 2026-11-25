"""TOPIC 1 - Database schema and demo data."""
from .core import *


def init_db():
    c = sqlite3.connect(DB)
    c.executescript("""
    create table if not exists users(id integer primary key, name text, email text unique, password text,
      role text, department text, reset_token text);
    create table if not exists equipment(id integer primary key, name text, category text, brand text, model_no text,
      serial_no text, department text, lab text, purchase_date text, purchase_cost real, warranty_expiry text,
      quantity integer, cond text, status text, image text, description text);
    create table if not exists requests(id integer primary key, equip_id integer, user_id integer, qty integer,
      status text, req_date text, issue_date text, due_date text, return_date text, purpose text);
    create table if not exists maintenance(id integer primary key, equip_id integer, date text, cost real, note text);
    """)
    if not c.execute("select 1 from users").fetchone():
        for n, e, r, d in [("Super Admin", "admin@college.edu", ROLES[0], "Administration"),
                           ("Dr. Meera (HOD)", "hod@college.edu", ROLES[2], "Computer Science"),
                           ("Ravi (Lab Asst)", "lab@college.edu", ROLES[3], "Electronics"),
                           ("Prof. Anand", "faculty@college.edu", ROLES[4], "Computer Science")]:
            c.execute("insert into users(name,email,password,role,department) values(?,?,?,?,?)",
                      (n, e, generate_password_hash("admin123"), r, d))
        random.seed(7)
        items = [("Desktop Computer", "Computers", "Dell", "Computer Science", "CS Lab 1", 40, 55000),
                 ("Laptop", "Computers", "HP", "Computer Science", "CS Lab 2", 15, 62000),
                 ("Oscilloscope", "Instruments", "Tektronix", "Electronics", "Electronics Lab", 8, 85000),
                 ("Digital Multimeter", "Instruments", "Fluke", "Electronics", "Electronics Lab", 25, 6500),
                 ("3D Printer", "Fabrication", "Creality", "Mechanical", "Workshop", 2, 120000),
                 ("Projector", "AV", "Epson", "Administration", "Seminar Hall", 6, 48000),
                 ("Microscope", "Instruments", "Olympus", "Physics", "Physics Lab", 12, 30000),
                 ("Arduino Kit", "Electronics", "Arduino", "Electronics", "IoT Lab", 30, 3500),
                 ("Network Switch", "Networking", "Cisco", "Computer Science", "Network Lab", 4, 40000),
                 ("Spectrometer", "Instruments", "Agilent", "Chemistry", "Chem Lab", 3, 220000)]
        conds = ["Excellent", "Good", "Good", "Fair", "Poor", "Damaged"]
        for i, (n, cat, b, d, lab, qty, cost) in enumerate(items):
            pd = date.today() - timedelta(days=random.randint(100, 1800))
            cond = random.choice(conds)
            st = "Under Maintenance" if cond == "Poor" and random.random() < .5 else "Available"
            c.execute("insert into equipment(name,category,brand,model_no,serial_no,department,lab,purchase_date,"
                      "purchase_cost,warranty_expiry,quantity,cond,status,image,description) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                      (n, cat, b, f"M-{100+i}", f"SN{random.randint(10000,99999)}", d, lab, pd.isoformat(), cost,
                       (pd + timedelta(days=random.choice([365, 730, 1095]))).isoformat(), qty, cond, st, "", f"{b} {n}"))
            eid = i + 1
            for m in range(6):
                for _ in range(random.randint(0, 4)):
                    rd = date.today() - timedelta(days=m * 30 + random.randint(0, 25))
                    c.execute("insert into requests(equip_id,user_id,qty,status,req_date,issue_date,due_date,return_date,purpose)"
                              " values(?,?,?,?,?,?,?,?,?)", (eid, 4, random.randint(1, 3), "Returned", rd.isoformat(),
                              rd.isoformat(), (rd + timedelta(days=7)).isoformat(), (rd + timedelta(days=6)).isoformat(), "Practical session"))
            if i in (0, 2, 5):
                d0 = date.today() - timedelta(days=12)
                c.execute("insert into requests(equip_id,user_id,qty,status,req_date,issue_date,due_date,purpose) values(?,?,?,?,?,?,?,?)",
                          (eid, 4, 2, "Issued", d0.isoformat(), d0.isoformat(), (d0 + timedelta(days=7)).isoformat(), "Project work"))
            if cond in ("Poor", "Damaged", "Fair"):
                c.execute("insert into maintenance(equip_id,date,cost,note) values(?,?,?,?)",
                          (eid, (date.today() - timedelta(days=60)).isoformat(), random.randint(500, 8000), "Service"))
        c.execute("insert into requests(equip_id,user_id,qty,status,req_date,purpose) values(4,4,5,'Pending',?,'Lab exam')", (today(),))
        c.commit()
    c.close()

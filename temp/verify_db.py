import sqlite3

con = sqlite3.connect(r"C:\Users\Administrator\Desktop\Date\temp\cairn-p003.db")
tables = sorted(r[0] for r in con.execute("select name from sqlite_master where type='table'").fetchall())
print("TABLES:", tables)
for t in ("entities", "concepts", "domains", "relations"):
    if t in tables:
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"{t}: {n}")
con.close()
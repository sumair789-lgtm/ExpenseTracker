import sqlite3

class Database:
    def __init__(self,db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "Create Table IF NOT EXISTS expense_record(item_name text,item_price float, purchase_date date)"
        )

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS budget(
            amount REAL
        )
        """)

        self.conn.commit()

    def fetchRecord(self, query, params=()):
        self.cur.execute(query, params)
        return self.cur.fetchall()


    def insertRecord(self,item_name,item_price,purchase_date):
        self.cur.execute("INSERT INTO expense_record VALUES (?,?,?)",
                         (item_name,item_price,purchase_date))
        self.conn.commit()
    
    def removeRecord(self,rwid):
        self.cur.execute("DELETE FROM expense_record WHERE rowid=?" , (rwid,))
        self.conn.commit()
    
    def updateRecord(self,item_name,item_price,purchase_date,rowid):
        self.cur.execute("UPDATE expense_record SET item_name = ? , item_price = ?, purchase_date = ? WHERE rowid = ? ",
                         (item_name,item_price,purchase_date,rowid))
        self.conn.commit()
        
    def setBudget(self, amount):
        self.cur.execute("DELETE FROM budget")   # only one budget
        self.cur.execute("INSERT INTO budget VALUES (?)", (amount,))
        self.conn.commit()

    def getBudget(self):
        self.cur.execute("SELECT amount FROM budget")
        row = self.cur.fetchone()
        return row[0] if row else 0
        
    def __del__(self):
        self.conn.close()
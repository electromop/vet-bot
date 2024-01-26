import sqlite3
from datetime import date

class Database:

    def __init__(self, path):
        self.path = path
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS employees (chat_id TEXT PRIMARY KEY, role TEXT NOT NULL, username TEXT, phone TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS requests (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, excel_num INT, open_date TIMESTAMP NOT NULL, close_date TIMESTAMP, animal_type TEXT NOT NULL, adress TEXT NOT NULL, description TEXT NOT NULL, contacts TEXT NOT NULL, op_id TEXT NOT NULL, doc_id TEXT)")
        con.commit()
        cur.close()
        con.close()

    def get_user_role(self, chat_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT role FROM employees WHERE chat_id=?", (chat_id, ))
        role = cur.fetchone()
        cur.close()
        con.close()
        if role == None:
            return None
        else:
            return role[0]
    
    def add_user(self, chat_id, role):
        try:
            con = sqlite3.connect(self.path)
            cur = con.cursor()
            cur.execute("INSERT INTO employees (chat_id, role) VALUES (?, ?)", (chat_id, role, ))
            con.commit()
            cur.close()
            con.close()
            return 'success'
        except:
            cur.close()
            con.close()
            self.del_user(chat_id)
            self.add_user(chat_id, role)
            return "success"
    
    def add_contacts(self, chat_id, number, username):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("UPDATE employees SET phone=?, username=? WHERE chat_id=?", (number, username, chat_id, ))
        con.commit()
        cur.close()
        con.close()
        return 'success'
    
    def get_contacts(self, chat_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT phone, username FROM employees WHERE chat_id=?", (chat_id, ))
        contacts = dict(zip(["phone","username"], list(cur.fetchone())))
        con.commit()
        cur.close()
        con.close()
        return contacts
    
    def del_user(self, chat_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("DELETE FROM employees WHERE chat_id=?", (chat_id, ))
        con.commit()
        cur.close()
        con.close()
    
    def get_users_by_role(self, role):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT chat_id FROM employees WHERE role=?", (role, ))
        ids_list = cur.fetchall()
        con.commit()
        cur.close()
        con.close()
        return ids_list
    
    def get_request(self, request_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT * FROM requests WHERE id=?", (request_id,))
        request = cur.fetchone()
        names = list(map(lambda x: x[0], cur.description))
        cur.close()
        con.close()
        return dict(zip(list(names), list(request))) 

    def add_request(self, animal_type, contacts, adress, description, op_id, doc_id=None, close_date=None, excel_num=None):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        open_date = date.today()
        cur.execute("INSERT INTO requests (excel_num, open_date, close_date, animal_type, adress, description, contacts, op_id, doc_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (excel_num, open_date, close_date, animal_type, adress, description, contacts, op_id, doc_id,))
        con.commit()
        request_id = cur.lastrowid
        cur.close()
        con.close()
        return request_id
    
    def set_doc_on_request(self, request_id, doc_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("UPDATE requests SET doc_id=? WHERE id=?", (doc_id, request_id,))
        con.commit()
        cur.close()
        con.close()
    
    def set_excel_num(self, request_id, num):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("UPDATE requests SET excel_num=? WHERE id=?", (num, request_id,))
        con.commit()
        cur.close()
        con.close()
    
    def set_close_date_on_request(self, request_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        close_date = date.today()
        cur.execute("UPDATE requests SET close_date=? WHERE id=?", (close_date, request_id,))
        con.commit()
        cur.close()
        con.close()

    def is_accepted(self, request_id):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute("SELECT doc_id FROM requests WHERE id=?", (int(request_id),))
        request_state = cur.fetchone()
        con.commit()
        cur.close()
        con.close()
        return False if request_state[0] == None else True

class Keyboard:

    def __init__(self, kb_dict, row_width):
        self.kb_dict = kb_dict
        self.row_width = row_width
        
    def gen(self):
        pass

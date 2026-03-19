import sqlite3

def init_db():
    conn = sqlite3.connect("joseph_core.db")
    cursor = conn.cursor()
    # جدول المستخدمين وبصمة الوجه
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                     (username TEXT PRIMARY KEY, password TEXT, face_id TEXT)''')
    # جدول الرسائل والسياق
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                     (username TEXT, role TEXT, content TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

import mysql.connector
import bcrypt

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="##96Ee30",
    database="CAPSTONE"
)
cursor = db.cursor()

loginid = "102206089"
raw_password = "xyz"
hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
query = "INSERT INTO logins (loginids, passwords) VALUES (%s, %s)"
cursor.execute(query, (loginid, hashed_password))
db.commit()
cursor.close()
db.close()

print("User inserted!")

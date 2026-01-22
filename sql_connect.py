import mysql.connector

# Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="##96Ee30"
)

# Create a cursor
mycursor = mydb.cursor()

# Execute the SHOW DATABASES command
mycursor.execute("USE CAPSTONE")
mycursor.execute("select * from logins")

# Print all databases
for db in mycursor:
    print(db)

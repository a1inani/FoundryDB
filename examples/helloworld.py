from foundrydb import Database

db = Database()
db.execute("CREATE TABLE users (id INT, name TEXT);")
db.execute("INSERT INTO users VALUES (1, 'Alice');")
rows = db.execute("SELECT * FROM users;")
print(rows)

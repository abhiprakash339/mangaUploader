import sqlite3

bot_db = sqlite3.connect('exp.db')

# bot_db_cursor = bot_db.cursor()
# bot_db_cursor.execute('''CREATE TABLE stocks(date text, trans text, symbol text, qty real, price real)''')
# bot_db_cursor.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
# bot_db.commit()
# bot_db.close()
for i in bot_db.execute('SELECT * FROM stocks'):
    print(i)
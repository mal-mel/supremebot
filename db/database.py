import sqlite3


CONNECTION = sqlite3.connect('db/user_database.db')
DB = CONNECTION.cursor()

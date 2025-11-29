from peewee import SqliteDatabase
import os

# Set up your database connection
db = SqliteDatabase('chat.db')

db.connect(reuse_if_open=True)

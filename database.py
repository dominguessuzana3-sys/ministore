# database.py
import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'ministore'),
        password=os.environ.get('DB_PASSWORD', '123mudar'),
        database=os.environ.get('DB_NAME', 'ministore')
    )
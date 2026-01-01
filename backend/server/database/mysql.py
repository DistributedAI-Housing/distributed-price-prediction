import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",        # vide par défaut XAMPP
        database="real_estate_db"
    )

import mysql.connector

try:
    # Connexion à MySQL via XAMPP
    conn = mysql.connector.connect(
        host="localhost",
        user="root",       # utilisateur par défaut
        password="",       # mot de passe par défaut
        database="real_estate_db"  # nom de la DB que tu veux tester
    )

    if conn.is_connected():
        print("Connexion réussie à MySQL via XAMPP !")
        cursor = conn.cursor()
        cursor.execute("SELECT DATABASE();")
        print("Base utilisée :", cursor.fetchone())

except mysql.connector.Error as err:
    print("Erreur :", err)

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()

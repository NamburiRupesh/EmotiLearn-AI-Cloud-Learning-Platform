import mysql.connector


def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rupesh@2007",
        database="emotilearn_db"
    )

    return connection

import mysql.connector


def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MiracleTanya1127",
        database="carbon_footprint"
    )

    return conn
import MySQLdb


def connection():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="Chubasic747", db="44ENDWAY")
    c = conn.cursor()
    return c, conn

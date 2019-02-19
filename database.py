# Import libraries
import mysql.connector
import connection as connection

cnx = ''
cursor = ''


def connect():
    global cnx, cursor
    cnx = mysql.connector.connect(user=connection.u, password=connection.p, host=connection.h, database=connection.d)
    cursor = cnx.cursor(buffered=True)


def disconnect():
    global cnx, cursor
    cursor.close()
    cnx.close()


def multiquery(query, params):
    global cnx, cursor
    results = cursor.execute(query, params, multi=True)
    if -1 == cursor.rowcount:
        return cursor
    else:
        for cur in results:
            if cur.with_rows:
                records = cur.fetchall()
    cnx.commit()
    return records


def query(query, params):
    global cnx, cursor
    cursor.execute(query, params)
    cnx.commit()
    return cursor


def warnings():
    global cnx, cursor
    return cursor.fetchwarnings()

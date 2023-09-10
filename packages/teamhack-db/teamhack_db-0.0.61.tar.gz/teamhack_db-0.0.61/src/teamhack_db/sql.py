#from psycopg2 import connect

def drop_type_record(conn): # TODO delete this
    with conn.cursor() as curs:
        curs.execute("""DROP TYPE IF EXISTS record_type""")
def drop_table(conn):
    with conn.cursor() as curs:
        curs.execute("""DROP TABLE IF EXISTS hosts""")
    drop_type_record(conn)

#def create_type_record(conn):
#    with conn.cursor() as curs:
#        curs.execute("""CREATE TYPE record_type AS ENUM ('A', 'AAAA', 'MX', 'NS')""")
def create_table(conn):
    #create_type_record(conn)
    with conn.cursor() as curs:
      curs.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
          id       SERIAL        PRIMARY KEY,
          hostname VARCHAR(255)  NOT NULL,
          record   INT           NOT NULL,
          ip       INET          NOT NULL,
          UNIQUE(hostname, record)
        )
      """)

def insert(conn, hostname, record, ip):
    sql = """INSERT INTO hosts (hostname, record, ip) VALUES (%s, %s, %s)"""
    with conn.cursor() as curs:
        curs.execute(sql, (hostname, record, ip,))

def select(conn):
    with conn.cursor() as curs:
        curs.execute("""SELECT hostname, record, ip FROM hosts""")
        return curs.fetchall()

def select_ip(conn, ip):
    with conn.cursor() as curs:
        curs.execute("""SELECT * FROM hosts WHERE ip = %s""", (ip,))
        return curs.fetchall()
def select_hostname(conn, hostname):
    with conn.cursor() as curs:
        curs.execute("""SELECT * FROM hosts WHERE hostname = %s""", (hostname,))
        return curs.fetchall()
def select_hostname_recordtype(conn, hostname, record):
    with conn.cursor() as curs:
        curs.execute("""SELECT * FROM hosts WHERE hostname = %s AND record = %s""", (hostname, record))
        return curs.fetchone()

def drop_row_id(conn, row_id):
    with conn.cursor() as curs:
        curs.execute("""DELETE FROM hosts WHERE id = %s""", (row_id,))
def drop_row_hostname(conn, hostname):
    with conn.cursor() as curs:
        curs.execute("""DELETE FROM hosts WHERE hostname = %s""", (hostname,))
def drop_row_ip(conn, ip):
    with conn.cursor() as curs:
        curs.execute("""DELETE FROM hosts WHERE ip = %s""", (ip,))


import sqlite3
from sqlite3 import Error
import jenkins
import datetime


db = "jenkins.db"
url = "http://localhost:8080"
username = "your_username"
password = "your_password"



def db_connect(db_file):
    """ create SQLite database if not exist """
    try:
        conn = sqlite3.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        return conn
    except Error as e:
        print(e)


def create_schema(conn):
    """ create SQLite database tables if not exist """
    try:
        conn.execute("CREATE TABLE job (id integer primary key, name TEXT UNIQUE ON CONFLICT IGNORE, status TEXT, [timestamp] timestamp)")
        conn.commit()
    except Error as e:
        print(e)


def get_jobs_from_db(conn):
    try:
        cur = conn.cursor()
        jobs = cur.execute("SELECT * FROM job").fetchall()
        return jobs
    except Error as e:
        print(e)
        exit()


def connect_to_jenkins(url, username, password):
    try:
        server = jenkins.Jenkins(url, username, password, timeout=5)
        return server
    except:
        print("error connecting to jenkins instance")
        print("exiting the script")
        exit()


def get_jobs_from_server(server):
    user = server.get_whoami()
    version = server.get_version()
    print('Hello %s from Jenkins %s' % (user['fullName'], version))
    jobs = server.get_jobs()
    return jobs


def jobs_loop(conn, jobs, db_jobs):
    c = conn.cursor()
    if len(jobs) != 0:
        for job in jobs:
            c.execute("REPLACE INTO job (name, status, timestamp) VALUES (?, ?, ?)", (job["fullname"], job["color"], datetime.datetime.now()))
        conn.commit()
        print("records saved in db")
    else:
        print("NO JOBS FOUND IN SERVER")


if __name__ == '__main__':
    server = connect_to_jenkins(url, username, password)
    jobs = get_jobs_from_server(server)

    try:
        conn = db_connect(db)
        create_schema(conn)
        db_jobs = get_jobs_from_db(conn)
        jobs_loop(conn, jobs, db_jobs)

    except Error as e:
        print(e)
    
    finally:
        conn.close()

    print("all is fine gonna exit now")
    exit()

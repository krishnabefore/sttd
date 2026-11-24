"""One-time setup: creates the project's MySQL login and loads the sample data.
Run by setup.bat. Your MySQL root password is typed once and is never saved."""
import getpass
import os
import subprocess
import sys

import mysql.connector
from mysql.connector import Error

HERE = os.path.dirname(os.path.abspath(__file__))
HOST = os.getenv('DB_HOST', 'localhost')
USER = 'cognipath'
PASSWORD = 'cognipath'


def main():
    print('StudyPath setup')
    print('Enter your MySQL root password (typing is hidden and it is not saved).')
    root_password = getpass.getpass('MySQL root password: ')

    try:
        conn = mysql.connector.connect(host=HOST, user='root', password=root_password)
    except Error as e:
        print(f'\nCould not log in to MySQL: {e}')
        print('Check that the MySQL service is running and that the password is right.')
        sys.exit(1)

    cur = conn.cursor()
    cur.execute(f"CREATE USER IF NOT EXISTS '{USER}'@'localhost' IDENTIFIED BY '{PASSWORD}'")
    cur.execute(f"ALTER USER '{USER}'@'localhost' IDENTIFIED BY '{PASSWORD}'")
    cur.execute(f"GRANT ALL PRIVILEGES ON studypath.* TO '{USER}'@'localhost'")
    cur.execute('FLUSH PRIVILEGES')
    conn.close()
    print(f"MySQL login '{USER}' is ready.")

    env = dict(os.environ, DB_USER=USER, DB_PASSWORD=PASSWORD)
    result = subprocess.run([sys.executable, 'seed.py'], cwd=HERE, env=env)
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
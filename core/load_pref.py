'''preferences'''
import os, sys
import sqlite3

from src.global_constants import __disk_path__
from exceptions.odno_exceptions import OdnoException

__conn_str = ".resources/user_pref.db"
# _conn:sqlite3.Connection = sqlite3.connect(__conn_str)

def __get_connection() -> sqlite3.Cursor:
    conn = sqlite3.connect(__conn_str)
    return conn.cursor()

def is_first_run() -> bool:
    '''Check if db objects exist.'''
    c = __get_connection()

    return c.execute('''
    SELECT tableName FROM sqlite_master WHERE type='table'
    AND tableName='USER_PREFS';
    ''').fetchall() != []

def init_db():
    '''init db file'''
    try:
        _conn = sqlite3.connect(__conn_str)
        c = _conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS USER_PREFS (
                MUSIC_PATH TEXT,
                DISK TEXT,
                FIRST_RUN INTEGER
            );
        ''')
        mpath = f'{os.path.expanduser("~")}/Music'
        query = f'INSERT INTO USER_PREFS (MUSIC_PATH, DISK, FIRST_RUN) VALUES ("{mpath}", "{__disk_path__()}", 0);'
        query = query.replace("/", "_slash_").replace(":", "_colon_").replace("=", "_equal_")
        c.execute(query)

        _conn.commit()
        _conn.close()
    except sqlite3.OperationalError as e:
        __sql_error(_conn, e)

    finally:
        _conn.close()

def get_prefs() -> dict:
    '''get user preferences from sqlite file'''
    prefs = __get_connection().execute("SELECT * FROM USER_PREFS;").fetchall()

    if not prefs:
        return {"error": "could not open db file."}

    pref_tuple = prefs[0]
    return {
        "MUSIC_PATH" : pref_tuple[0].replace("_slash_", "/"),
        "DISK" : pref_tuple[1].replace("_slash_", "/").replace("_colon_", ":").replace("_equal_", "="),
        "FIRST_RUN": pref_tuple[2]
    }

def update_prefs(prefs: dict) -> dict:

    query = '''
        UPDATE USER_PREFS
        SET MUSIC_PATH = ?, DISK = ?, FIRST_RUN = 0
    '''
    _conn = sqlite3.connect(__conn_str)

    try:
        update:sqlite3.Cursor = _conn.cursor().execute(query, (prefs["MUSIC_PATH"], prefs["DISK"]))

        if update:
            _conn.commit()
            print("saved!")

    except (sqlite3.OperationalError) as e:
        __sql_error(_conn, e)

    finally:
        _conn.close()
    


def __sql_error(_conn:sqlite3.Connection, e: sqlite3.OperationalError):
    '''handle sqlite3 error'''
    print("something went wrong...")
    OdnoException.handle_exception(OdnoException("failed to create user_pref file", e), e.sqlite_errorname, "core.pref.init_db")
    os.remove("user_pref.db")
    _conn.rollback()
    sys.exit()

def start_up():
    '''create db object if sqlite file does not exist'''
    if not os.path.isfile("user_pref.db") or is_first_run():
        init_db()

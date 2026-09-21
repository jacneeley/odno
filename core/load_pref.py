'''preferences'''
import os, sys
import sqlite3
import subprocess

from core.cmds import install_dependencies
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
                DISK TEXT
            );
        ''')
        mpath = f'{os.path.expanduser("~")}/Music'
        query = f'INSERT INTO USER_PREFS (MUSIC_PATH, DISK) VALUES ("{mpath}", "{__disk_path__()}");'
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
    try:
        prefs = __get_connection().execute("SELECT * FROM USER_PREFS;").fetchall()

        pref_tuple = prefs[0]
        return {
            "MUSIC_PATH" : pref_tuple[0].replace("_slash_", "/"),
            "DISK" : pref_tuple[1].replace("_slash_", "/").replace("_colon_", ":").replace("_equal_", "=")
        }
    except sqlite3.OperationalError:
        print("first init. installing dependencies...")
        init_db()
        install_dependencies()

def update_prefs(prefs: dict) -> dict:
    '''update user preferences'''
    query = '''
        UPDATE USER_PREFS
        SET MUSIC_PATH = ?, DISK = ?
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
    try:
        if not os.path.isfile(".resources/user_pref.db"):
            init_db()
            install_dependencies()

    except (subprocess.CalledProcessError) as e:
        oe = OdnoException(message="install failed", e=e)
        OdnoException.handle_exception(oe, oe.message, "load_pref.start_up")

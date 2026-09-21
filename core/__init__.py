'''core package.'''
from core.load_pref import start_up
from core.utility import clean_up_logs
from core.rip import init_device

from models.odno_cache import OdnoCache

start_up()

init_device()

clean_up_logs()

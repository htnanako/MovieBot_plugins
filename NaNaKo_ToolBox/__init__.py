from .app import *
from .command import *

now = datetime.datetime.now()
time_cache.set('start_time', now)
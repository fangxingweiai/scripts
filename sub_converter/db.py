import os

from deta import Deta

deta = Deta(os.environ['deta_key'])
user_db = deta.Base('user')
config_db = deta.Base('config')
me_db = deta.Base('me')

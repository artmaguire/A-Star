from decouple import config


class Config(object):
    DBNAME = config('DBNAME')
    DBUSER = config('DBUSER')
    DBPASSWORD = config('DBPASSWORD')
    DBHOST = config('DBHOST')
    DBPORT = config('DBPORT')

    EDGES_TABLE = config('EDGES_TABLE')
    VERTICES_TABLE = config('VERTICES_TABLE')


conf = Config()

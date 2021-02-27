from decouple import config


class Config(object):
    DBNAME = config('DBNAME')
    DBUSER = config('DBUSER')
    DBPASSWORD = config('DBPASSWORD')
    DBHOST = config('DBHOST')
    DBPORT = config('DBPORT')


conf = Config()

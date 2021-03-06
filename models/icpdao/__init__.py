# mongodb
import time

from mongoengine import connect, connection, Document
import logging

dbs = {}


def init_mongo(mongo_config):
    """
    Connect to mongo database
    mongo_config:
    {
        'icpdao': {
            'host': self.settings.ICPDAO_MONGODB_ICPDAO_HOST,
            'alias': 'icpdao',
        },
        'xxx': {
            'host': self.settings.ICPDAO_MONGODB_XXX_HOST,
            'alias': 'xxx',
        }
    }
    """
    global dbs
    for dbname, conn_config in mongo_config.items():
        alias = conn_config['alias']
        host = conn_config['host']
        logging.info('connect mongo {}'.format(alias))
        dbs[alias] = connect(alias=alias, host=host)


def disconnect_mongo():
    for dbalias, con in dbs.items():
        connection.disconnect(dbalias)


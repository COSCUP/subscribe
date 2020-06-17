from time import time

import pymongo
from pymongo.collection import Collection

import setting


class DBBase(Collection):
    ''' DBBase class

    :param str name: collection name

    '''
    def __init__(self, name):
        client = pymongo.MongoClient('mongodb://%s:%s' % (
                setting.MONGO_HOST, setting.MONGO_PORT))[setting.MONGO_DBNAME]

        super(DBBase, self).__init__(client, name)

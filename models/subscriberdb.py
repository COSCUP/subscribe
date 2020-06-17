from datetime import datetime
from uuid import uuid4

from models.base import DBBase


class SubscriberDB(DBBase):
    '''SubscriberDB class'''
    def __init__(self):
        super(SubscriberDB, self).__init__('subscriber')

    @staticmethod
    def default(uni_mail, name, mails):
        ''' default data '''
        return {
            '_id': uni_mail,
            'name': name,
            'mails': mails,
            'code': '%0.8x' % uuid4().fields[0],
            'created_at': datetime.now(),
        }

from datetime import datetime
from uuid import uuid4

from models.base import DBBase


class SubscriberDB(DBBase):
    ''' SubscriberDB collection '''

    def __init__(self):
        super(SubscriberDB, self).__init__('subscriber')

    def index(self):
        ''' index '''
        self.create_index([('status', 1), ])

    @staticmethod
    def default(uni_mail, name, mails):
        ''' default data '''
        return {
            '_id': uni_mail,
            'name': name,
            'mails': mails,
            'code': '%0.8x' % uuid4().fields[0],
            'ucode': '%0.8x' % uuid4().fields[0],
            'status': True,
            'verified_email': False,
            'created_at': datetime.now(),
        }


class SubscriberLoginTokenDB(DBBase):
    ''' SubscriberLoginTokenDB collection '''

    def __init__(self):
        super(SubscriberLoginTokenDB, self).__init__('subscriber_login_token')

    def index(self):
        ''' index '''
        self.create_index([('created_at', -1), ])

    @staticmethod
    def default(token, uni_mail, _type):
        ''' default data

        :param str _type: code, token, verify_mail

        '''
        return {
            '_id': token,
            'uni_mail': uni_mail,
            '_type': _type,
            'created_at': datetime.now(),
        }


class SubscriberReadDB(DBBase):
    ''' SubscriberReadDB collection '''

    def __init__(self):
        super(SubscriberReadDB, self).__init__('subscriber_read')

    def index(self):
        ''' index '''
        self.create_index([('created_at', -1), ])
        self.create_index([('topic', 1), ])

    @staticmethod
    def default(ucode, topic, headers, args=None):
        ''' default data

        :param str ucode: ucode
        :param str topic: topic
        :param dict headers: headers
        :param str args: args

        '''
        return {
            'ucode': ucode,
            'topic': topic,
            'headers': headers,
            'args': args,
            'created_at': datetime.now(),
        }


class OPassLogsDB(DBBase):
    ''' OPassLogsDB '''

    def __init__(self):
        super(OPassLogsDB, self).__init__('subscriber_opass_logs')

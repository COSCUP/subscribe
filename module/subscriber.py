import hashlib
import re
from datetime import datetime
from time import time
from uuid import uuid4

from pymongo.collection import ReturnDocument

from models.subscriberdb import SubscriberDB
from models.subscriberdb import SubscriberLoginTokenDB


class Subscriber(object):
    '''Subscriber class

    :param str mail: get subscriber data from mail

    '''
    def __init__(self, mail):
        mail = self.format_mail(mail)
        self.data = SubscriberDB().find_one({'_id': mail})

    def render_admin_code(self):
        ''' render admin code for link '''
        return self.shadata('%(code)s|%(_id)s' % self.data)

    def verify_admin_code(self, code):
        ''' verify admin code

        :param str code: code

        '''
        return code == self.render_admin_code()

    def make_login(self, _type):
        ''' make an login code

        :param str _type: code, token

        '''
        if _type not in ('code', 'token'):
            raise Exception('type error')

        token = self.shadata(str(uuid4()) + str(uuid4()))

        data = SubscriberLoginTokenDB.default(
                token=token, uni_mail=self.data['_id'], _type=_type)

        return SubscriberLoginTokenDB().insert_one(data).inserted_id

    @classmethod
    def verify_login(cls, _type, code):
        ''' verify login code

        :param str _type: code, token

        '''
        if _type == 'code':
            before = datetime.fromtimestamp(time() - 600)

        elif _type == 'token':
            before = datetime.fromtimestamp(time() - 3600)

        login_token = SubscriberLoginTokenDB().find_one(
                {'_id': code, '_type': _type, 'created_at': {'$gte': before}})

        if not login_token:
            return False

        return cls(mail=login_token['uni_mail'])

    @classmethod
    def process_upload(cls, mail, name):
        '''process upload

        :param str mail: mail
        :param str name: name

        '''
        mail = mail.strip().lower()
        uni_mail = cls.format_mail(mail=mail)

        if not uni_mail:
            return

        data = SubscriberDB().find_one({'_id': uni_mail})
        if data:
            _update = {'$addToSet': {'mails': mail}}

            name = name.strip()
            if name:
                _update['$set'] = {'name': name}

            SubscriberDB().update({'_id': uni_mail}, _update)
        else:
            insert_data = SubscriberDB.default(
                    uni_mail=uni_mail, name=name.strip(), mails=[mail, ])

            SubscriberDB().insert_one(insert_data)

    @staticmethod
    def format_mail(mail):
        '''format mail

           clean '.', '+', lower
        '''
        mail = mail.lower().strip()
        if '+' in mail:
            mail = re.sub(r'(\+[a-z0-9]+)@', '@', mail)

        _mail = mail.split('@')

        if '.' in _mail[0]:
            return '%s@%s' % (_mail[0].replace('.', ''), _mail[1])

        return mail

    @staticmethod
    def shadata(data):
        m = hashlib.sha256()
        m.update(data.encode('utf8'))

        return m.hexdigest()

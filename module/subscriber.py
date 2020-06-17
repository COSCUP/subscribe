import hashlib
import re

from models.subscriberdb import SubscriberDB


class Subscriber(object):
    '''Subscriber class'''
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
    def shamail(mail):
        mail = format_mail(mail)

        m = hashlib.sha256()
        m.update(mail.encode('utf8'))

        return m.hexdigest()

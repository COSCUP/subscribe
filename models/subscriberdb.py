''' SubscriberDB '''
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from models.base import DBBase


class SubscriberDB(DBBase):
    ''' SubscriberDB collection '''

    def __init__(self) -> None:
        super().__init__('subscriber')

    def index(self) -> None:
        ''' index '''
        self.create_index([('status', 1), ])

    @staticmethod
    def default(uni_mail: str, name: str, mails: list[str]) -> dict[str, Any]:
        ''' default data '''
        return {
            '_id': uni_mail,
            'name': name,
            'mails': mails,
            'code': f'{uuid4().fields[0]:08x}',
            'ucode': f'{uuid4().fields[0]:08x}',
            'status': True,
            'verified_email': False,
            'created_at': datetime.now(),
        }


class SubscriberLoginTokenDB(DBBase):
    ''' SubscriberLoginTokenDB collection '''

    def __init__(self) -> None:
        super().__init__('subscriber_login_token')

    def index(self) -> None:
        ''' index '''
        self.create_index([('created_at', -1), ])

    @staticmethod
    def default(token: str, uni_mail: str, _type: str) -> dict[str, Any]:
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

    def __init__(self) -> None:
        super().__init__('subscriber_read')

    def index(self) -> None:
        ''' index '''
        self.create_index([('created_at', -1), ])
        self.create_index([('topic', 1), ])

    @staticmethod
    def default(ucode: str, topic: str,
                headers: dict[str, Any], args: Optional[str] = None) -> dict[str, Any]:
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

    def __init__(self) -> None:
        super().__init__('subscriber_opass_logs')

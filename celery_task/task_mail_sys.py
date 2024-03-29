''' Task mail '''
# pylint: disable=unused-argument
from __future__ import absolute_import, unicode_literals

from time import time
from typing import Any

from celery.utils.log import get_task_logger

import setting
from celery_task.celery import app
from module.awsses import AWSSES
from module.sender import (SenderMailerSubscribeLoginCode,
                           SenderMailerSubscribeVerify)
from module.subscriber import Subscriber

logger = get_task_logger(__name__)


@app.task(bind=True, name='mail.sys.test',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cst.mail.sys.test', exchange='COSCUP-SECRETARY-TEAM')
def mail_sys_test(sender: Any, **kwargs: str) -> None:
    ''' mail sys test '''
    logger.info('!!! [%s]', kwargs)
    raise SystemError('Test in error and send mail.')


@app.task(bind=True, name='mail.sys.weberror',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cst.mail.sys.weberror', exchange='COSCUP-SECRETARY-TEAM')
def mail_sys_weberror(sender: Any, **kwargs: str) -> None:
    ''' mail_sys_weberror '''
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)

    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject=f"[COSCUP-SECRETARY-TEAM] {kwargs['title']}",
        body=kwargs['body'],
    )

    ses.send_raw_email(data=raw_mail)


@app.task(bind=True, name='mail.login.code',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cst.mail.login.code', exchange='COSCUP-SECRETARY-TEAM')
def mail_login_code(sender: Any, **kwargs: str) -> None:
    ''' mail_login_code '''
    user = Subscriber(mail=kwargs['mail'])
    if not user.data:
        logger.warning('No user data: %s', kwargs['mail'])

    subject = f'[Login] 管理 COSCUP 電子報訂閱連結 / Login for management subscription ({int(time())})'
    content = {
        'name': user.data['name'],
        'code': user.make_login(_type='code'),
        'preheader': 'Manage your subscriptions',
    }

    raw_mail = SenderMailerSubscribeLoginCode(subject=subject, content=content)

    name = user.data['name']
    if not name:
        name = user.data['mails'][-1]

    mail = user.data['mails'][-1]
    logger.info('mail: %s, ses: %s',
                mail,
                raw_mail.send(
                    to_list=[{'name': name, 'mail': mail}, ], data={}),
                )


@app.task(bind=True, name='mail.verify.mail',
          autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
          routing_key='cst.mail.verify.mail', exchange='COSCUP-SECRETARY-TEAM')
def mail_verify_mail(sender: Any, **kwargs: str) -> None:
    ''' mail_verify_mail '''
    user = Subscriber(mail=kwargs['mail'])
    if not user.data:
        logger.warning('No user data: %s', kwargs['mail'])
        return

    subject = f'[Verify] 驗證 COSCUP 電子報訂閱 / Your Subscription ({int(time())})'
    content = {
        'name': user.data['name'],
        'code': user.make_login(_type='verify_mail'),
        'preheader': 'Verification mail',
    }

    raw_mail = SenderMailerSubscribeVerify(subject=subject, content=content)

    name = user.data['name']
    if not name:
        name = user.data['mails'][-1]

    mail = user.data['mails'][-1]

    logger.info('mail: %s, ses: %s',
                mail,
                raw_mail.send(
                    to_list=[{'name': name, 'mail': mail}, ], data={}),
                )

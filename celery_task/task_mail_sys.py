from __future__ import absolute_import
from __future__ import unicode_literals

from time import time

from bson.objectid import ObjectId
from celery.utils.log import get_task_logger

import setting
from celery_task.celery import app
from module.awsses import AWSSES
from module.sender import SenderMailerSubscribeLoginCode
from module.sender import SenderMailerSubscribeVerify
from module.subscriber import Subscriber

logger = get_task_logger(__name__)

@app.task(bind=True, name='mail.sys.test',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.mail.sys.test', exchange='COSCUP-SECRETARY-TEAM')
def mail_sys_test(sender, **kwargs):
    logger.info('!!! [%s]' % kwargs)
    raise Exception('Test in error and send mail.')

@app.task(bind=True, name='mail.sys.weberror',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.mail.sys.weberror', exchange='COSCUP-SECRETARY-TEAM')
def mail_sys_weberror(sender, **kwargs):
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)

    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject='[COSCUP-SECRETARY-TEAM] %s' % kwargs['title'],
        body=kwargs['body'],
    )

    ses.send_raw_email(data=raw_mail)

@app.task(bind=True, name='mail.login.code',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.mail.login.code', exchange='COSCUP-SECRETARY-TEAM')
def mail_login_code(sender, **kwargs):
    user = Subscriber(mail=kwargs['mail'])
    if not user.data:
        logger.warn('No user data: %s', kwargs['mail'])

    subject = u'[Login] 管理 COSCUP 電子報訂閱連結 / Login for management subscription (%d)' % int(time())
    content = {
        'name': user.data['name'],
        'code': user.make_login(_type='code'),
        'preheader': '!!!',
    }

    raw_mail = SenderMailerSubscribeLoginCode(subject=subject, content=content)

    name = user.data['name']
    if not name:
        name = user.data['mails'][-1]

    mail = user.data['mails'][-1]
    logger.info('mail: %s, ses: %s',
        mail,
        raw_mail.send(to_list=({'name': name, 'mail': mail}, ), data={}),
    )

@app.task(bind=True, name='mail.verify.mail',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.mail.verify.mail', exchange='COSCUP-SECRETARY-TEAM')
def mail_verify_mail(sender, **kwargs):
    user = Subscriber(mail=kwargs['mail'])
    if not user.data:
        logger.warn('No user data: %s', kwargs['mail'])

    subject = u'[Verify] 驗證 COSCUP 電子報訂閱 / Your Subscription (%d)' % int(time())
    content = {
        'name': user.data['name'],
        'code': user.make_login(_type='verify_mail'),
        'preheader': '!!!',
    }

    raw_mail = SenderMailerSubscribeVerify(subject=subject, content=content)

    name = user.data['name']
    if not name:
        name = user.data['mails'][-1]

    mail = user.data['mails'][-1]

    logger.info('mail: %s, ses: %s',
        mail,
        raw_mail.send(to_list=({'name': name, 'mail': mail}, ), data={}),
    )

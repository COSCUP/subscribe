from __future__ import absolute_import
from __future__ import unicode_literals

from bson.objectid import ObjectId
from celery.utils.log import get_task_logger
from module.awsses import AWSSES

import setting
from celery_task.celery import app

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

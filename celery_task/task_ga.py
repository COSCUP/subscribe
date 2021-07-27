from __future__ import absolute_import
from __future__ import unicode_literals

from celery.utils.log import get_task_logger

import setting
from celery_task.celery import app
from module.ga import GaConn

logger = get_task_logger(__name__)

@app.task(bind=True, name='ga.reader',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.ga.reader', exchange='COSCUP-SECRETARY-TEAM')
def ga_reader(sender, **kwargs):
    GaConn(**setting.GA).event_mail_open(
            ucode=kwargs['ucode'],
            topic=kwargs['topic'],
            timestamp_micros=kwargs['timestamp_micros'],
        )

    logger.info(kwargs)

@app.task(bind=True, name='ga.subscribe',
    autoretry_for=(Exception, ), retry_backoff=True, max_retries=5,
    routing_key='cst.ga.subscribe', exchange='COSCUP-SECRETARY-TEAM')
def ga_subscribe(sender, **kwargs):
    GaConn(**setting.GA).event_mail_subscribe(
            ucode=kwargs['ucode'],
            timestamp_micros=kwargs['timestamp_micros'],
        )

    logger.info(kwargs)

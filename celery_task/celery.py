''' Celery '''
from __future__ import absolute_import, unicode_literals

from typing import Any

from celery import Celery
from celery.signals import task_failure
from kombu import Exchange, Queue

import setting
from module.awsses import AWSSES

app = Celery(
    main='celery_task',
    broker=f'amqp://{setting.RABBITMQ}',
    include=(
        'celery_task.task_mail_sys',
        'celery_task.task_ga',
    ),
)

app.conf.task_queues = (
    Queue('celery', Exchange('celery', type='direct'), routing_key='celery'),
    Queue('CST_mail', Exchange('COSCUP-SECRETARY-TEAM',
          type='topic'), routing_key='cst.mail.#'),
    Queue('CST_ga', Exchange('COSCUP-SECRETARY-TEAM',
          type='topic'), routing_key='cst.ga.#'),
)

app.conf.acks_late = True
app.conf.task_ignore_result = True
app.conf.worker_prefetch_multiplier = 2
app.conf.accept_content = ('json', 'pickle')


@task_failure.connect
def on_failure(**kwargs: Any) -> None:
    ''' on failure '''
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)
    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject=f"[COSCUP-SECRETARY-TEAM] {kwargs['sender'].name} [{kwargs['sender'].request.id}]",
        body=f"""kwargs: <pre>{kwargs['kwargs']}</pre><br>
einfo: <pre>{kwargs['einfo'].traceback}</pre><br>
request: <pre>{kwargs['sender'].request}</pre>""",
    )
    ses.send_raw_email(data=raw_mail)

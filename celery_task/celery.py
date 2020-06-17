from __future__ import absolute_import
from __future__ import unicode_literals

from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure
from kombu import Exchange, Queue, binding

from module.awsses import AWSSES

import setting

app = Celery(
    main='celery_task',
    broker='amqp://%s' % setting.RABBITMQ,
    include=(
        'celery_task.task_mail_sys',
    ),
)

app.conf.task_queues = (
    Queue('celery', Exchange('celery', type='direct'), routing_key='celery'),
    Queue('CST_mail', Exchange('COSCUP-SECRETARY-TEAM', type='topic'), routing_key='cst.mail.#'),
)

app.conf.acks_late = True
app.conf.task_ignore_result = True
app.conf.worker_prefetch_multiplier = 2
app.conf.accept_content = ('json', 'pickle')

@task_failure.connect
def on_failure(**kwargs):
    ses = AWSSES(setting.AWS_ID, setting.AWS_KEY, setting.AWS_SES_FROM)
    raw_mail = ses.raw_mail(
        to_addresses=[setting.ADMIN_To, ],
        subject='[COSCUP-SECRETARY-TEAM] %s [%s]' % (kwargs['sender'].name, kwargs['sender'].request.id),
        body='kwargs: <pre>%s</pre><br>einfo: <pre>%s</pre><br>request: <pre>%s</pre>' % (
            kwargs['kwargs'], kwargs['einfo'].traceback, kwargs['sender'].request),
    )
    ses.send_raw_email(data=raw_mail)

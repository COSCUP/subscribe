import logging

import requests
from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import setting
from celery_task.task_mail_sys import mail_verify_mail
from models.subscriberdb import SubscriberDB
from module.subscriber import Subscriber

VIEW_SUBSCRIBE = Blueprint('subscribe', __name__, url_prefix='/subscribe')

@VIEW_SUBSCRIBE.route('/coscup', methods=('GET', 'POST'))
def coscup():
    ''' subscribe coscup '''
    if request.method == 'GET':
        user_count = SubscriberDB().count_documents({'status': True})
        return render_template('./subscribe_coscup.html', user_count=user_count)

    elif request.method == 'POST':
        if not request.form['iamok']:
            session['show_info'] = ('006', )
            session['status_code'] = 401
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        r = requests.post('https://hcaptcha.com/siteverify',
                data={'response': request.form['h-captcha-response'],
                      'secret': setting.HCAPTCHA_TOKEN,
                      'remoteip': request.headers.get('X-REAL-IP')}).json()

        logging.info('hcaptcha: %s', r)

        if not (r['success'] and r['hostname'] == 'coscup.org'):
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        user = Subscriber(mail=request.form['mail'])
        Subscriber.process_upload(mail=request.form['mail'], name=request.form['name'])
        if not user.data:
            user = Subscriber(mail=request.form['mail'])
            mail_verify_mail.apply_async(kwargs={'mail': user.data['_id']})

        elif user.data:
            if not user.data['verified_email']:
                mail_verify_mail.apply_async(kwargs={'mail': user.data['_id']})

            if not user.data['status']:
                user.update_date({'status': True})

        session['show_info'] = ('007', )
        session['status_code'] = 200
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    return u''

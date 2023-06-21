''' subscribe '''
import json
import logging
from datetime import datetime

import requests
from flask import (Blueprint, jsonify, redirect, render_template, request,
                   session, url_for)
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_ga import ga_subscribe
from celery_task.task_mail_sys import mail_verify_mail
from models.subscriberdb import OPassLogsDB, SubscriberDB
from module.subscriber import Subscriber

VIEW_SUBSCRIBE = Blueprint('subscribe', __name__, url_prefix='/subscribe')


def process_subscribe(mail: str, name: str) -> Subscriber:
    ''' Process subscribe '''
    user = Subscriber(mail=mail)
    Subscriber.process_upload(mail=mail, name=name)
    if not user.data:
        user = Subscriber(mail=mail)
        mail_verify_mail.apply_async(kwargs={'mail': user.data['_id']})

    elif user.data:
        if not user.data['verified_email']:
            mail_verify_mail.apply_async(kwargs={'mail': user.data['_id']})

        if not user.data['status']:
            user.update_date({'status': True})

    return user


@VIEW_SUBSCRIBE.route('/coscup/opass', methods=('POST', ))
def coscup_opass() -> str | ResponseBase:
    ''' subscribe coscup via opass'''
    if request.method == 'POST':
        resp = requests.post('https://hcaptcha.com/siteverify',
                             timeout=10,
                             data={'response': request.form['h-captcha-response'],
                                   'secret': setting.HCAPTCHA_TOKEN,
                                   'remoteip': request.headers.get('X-REAL-IP')}).json()

        logging.info('[opass] hcaptcha: %s', resp)

        if not resp['success']:
            return Response(
                response=json.dumps({'error-codes': resp.get('error-codes')}),
                status=400,
                mimetype='application/json',
            )

        if not 'onlytoken' in request.form:
            process_subscribe(
                mail=request.form['mail'].strip(), name=request.form['name'].strip())

        opass_resp = requests.post('https://ccip.opass.app/import',
                                   timeout=10,
                                   data={'name': request.form['name'].strip()}
                                   ).json()

        logging.info('[opass] token: %s', opass_resp)

        log_data = {
            'name': request.form['name'].strip(),
            'mail': '',
            'opass_resp': opass_resp,
            'hcaptcha': resp,
            'remoteip': request.headers.get('X-REAL-IP'),
            'create_at': datetime.now(),
        }

        if not 'onlytoken' in request.form:
            log_data['mail'] = request.form['mail'].strip()

        OPassLogsDB().insert_one(log_data)

        return jsonify(opass_resp)

    return ''


@VIEW_SUBSCRIBE.route('/coscup', methods=('GET', 'POST'))
def coscup() -> str | ResponseBase:
    ''' subscribe coscup '''
    if request.method == 'GET':
        user_count = SubscriberDB().count_documents({'status': True})
        return render_template('./subscribe_coscup.html', user_count=user_count)

    if request.method == 'POST':
        if not request.form['iamok']:
            session['show_info'] = ('006', )
            session['status_code'] = 401
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        resp = requests.post('https://hcaptcha.com/siteverify',
                             timeout=10,
                             data={'response': request.form['h-captcha-response'],
                                   'secret': setting.HCAPTCHA_TOKEN,
                                   'remoteip': request.headers.get('X-REAL-IP')}).json()

        logging.info('hcaptcha: %s', resp)

        if not (resp['success'] and resp['hostname'] == 'coscup.org'):
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        user = process_subscribe(
            mail=request.form['mail'], name=request.form['name'])

        session['show_info'] = ('007', )
        session['status_code'] = 200

        ga_subscribe.apply_async(kwargs={
            'ucode': user.data['ucode'],
            'timestamp_micros': int(datetime.now().timestamp()*1000000),
        })

        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    return ''

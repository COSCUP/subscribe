''' subscriber '''
import logging

import requests
from flask import (Blueprint, jsonify, make_response, redirect,
                   render_template, request, session, url_for)
from flask.wrappers import Response
from werkzeug.wrappers import Response as ResponseBase

import setting
from celery_task.task_mail_sys import mail_login_code
from models.subscriberdb import SubscriberLoginTokenDB
from module.subscriber import Subscriber

VIEW_SUBSCRIBER = Blueprint('subscriber', __name__, url_prefix='/subscriber')


@VIEW_SUBSCRIBER.route('/infomsg')
def info_msg() -> ResponseBase:
    ''' info message '''
    if request.args.get('all'):
        show_info = ('000', )
    else:
        show_info = session.get('show_info', [])

    return Response(
        response=render_template(
            './subscriber_error.html', show_info=show_info),
        status=session.get('status_code', 401),
        mimetype='text/html',
    )


@VIEW_SUBSCRIBER.route('/code/<code>', methods=('GET', 'POST'))
def code_page(code: str) -> str | ResponseBase:
    ''' code page '''
    # pylint: disable=too-many-return-statements
    if request.method == 'GET':
        return render_template('./subscriber.html')

    if request.method == 'POST':
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

        ser = Subscriber(mail=request.form['mail'])
        if not ser or not ser.data:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        if not ser.data['status']:
            session['show_info'] = ('008', )
            session['status_code'] = 200
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        if ser.verify_admin_code(code):
            mail_login_code.apply_async(kwargs={'mail': ser.data['_id']})

            session['show_info'] = ('002', )
            session['status_code'] = 200
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        session['show_info'] = ('001', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    return ''


@VIEW_SUBSCRIBER.route('/token/<code>')
def token_code(code: str) -> str | ResponseBase:
    ''' token '''
    if request.method == 'GET':
        ser = Subscriber.verify_login(_type='code', code=code)
        if not ser or not ser.data:  # type: ignore
            session['show_info'] = ('003', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        Subscriber.make_code_disabled(code=code)
        session['s_login_token'] = ser.make_login('token')  # type: ignore

        return redirect(url_for('subscriber.intro', _scheme='https', _external=True))

    return ''


@VIEW_SUBSCRIBER.route('/verify_mail/<code>', methods=('GET', 'POST'))
def verify_mail(code: str) -> str | ResponseBase:
    ''' verify mail '''
    # pylint: disable=too-many-return-statements
    if request.method == 'GET':
        token = SubscriberLoginTokenDB().find_one({'_id': code})
        if not token:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        ser = Subscriber(mail=token['uni_mail'])
        if not ser or not ser.data:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        if ser.data['verified_email']:
            session['show_info'] = ('005', )
            session['status_code'] = 200
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        return render_template('./subscriber_verify_mail.html')

    if request.method == 'POST':
        if not request.form['iamok']:
            return make_response({}, 401)

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

        token = SubscriberLoginTokenDB().find_one({'_id': code})
        if not token:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        ser = Subscriber(mail=token['uni_mail'])
        if not ser or not ser.data:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        ser.verify_login(_type='verify_mail', code=code)

        session['show_info'] = ('005', )
        session['status_code'] = 200
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    return ''


@VIEW_SUBSCRIBER.route('/intro', methods=('GET', 'POST'))
def intro() -> str | ResponseBase:
    ''' intro '''
    # pylint: disable=too-many-return-statements
    if 's_login_token' not in session:
        session['show_info'] = ('003', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    user = Subscriber.verify_login(
        _type='token', code=session['s_login_token'])
    if not user or not user.data:  # type: ignore
        session['show_info'] = ('003', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./subscriber_intro.html')

    if request.method == 'POST':
        post_data = request.get_json()

        if 'casename' not in post_data:
            return make_response({}, 401)

        if post_data['casename'] == 'get':
            user_data = user.data  # type:ignore
            user_login_token_data = user.login_token_data  # type:ignore
            data = {
                'name': user_data['name'],
                'mails': user_data['mails'],
                'login_since': user_login_token_data['created_at'],
                'unsubscribe': not user_data['status'],
            }
            return jsonify({'data': data})

        if post_data['casename'] == 'update':
            data = post_data['data']

            update = {}
            update['name'] = data['name'].strip()
            update['status'] = not bool(data['unsubscribe'])

            user.update_date(data=update)  # type: ignore

            return jsonify({})

    return ''


@VIEW_SUBSCRIBER.route('/clean', methods=('GET', 'POST'))
def clean() -> ResponseBase:
    ''' clean '''
    session.pop('s_login_token', None)

    session['show_info'] = ('004', )
    session['status_code'] = 200
    return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

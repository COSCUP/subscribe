import logging

import requests
from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import setting
from celery_task.task_mail_sys import  mail_login_code
from module.subscriber import Subscriber

VIEW_SUBSCRIBER = Blueprint('subscriber', __name__, url_prefix='/subscriber')

@VIEW_SUBSCRIBER.route('/infomsg')
def info_msg():
    return render_template('./subscriber_error.html',
            show_info=session.get('show_info', [])), session.get('status_code', 401)

@VIEW_SUBSCRIBER.route('/code/<code>', methods=('GET', 'POST'))
def code_page(code):
    if request.method == 'GET':
        return render_template('./subscriber.html')

    elif request.method == 'POST':
        r = requests.post('https://hcaptcha.com/siteverify',
                data={'response': request.form['h-captcha-response'],
                      'secret': setting.HCAPTCHA_TOKEN,
                      'remoteip': request.headers.get('X-REAL-IP')}).json()

        logging.info('hcaptcha: %s', r)

        if not (r['success'] and r['hostname'] == 'coscup.org'):
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        s = Subscriber(mail=request.form['mail'])
        if not s.data:
            session['show_info'] = ('001', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        if s.verify_admin_code(code):
            mail_login_code.apply_async(kwargs={'mail': s.data['_id']})

            session['show_info'] = ('002', )
            session['status_code'] = 200
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        session['show_info'] = ('001', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

@VIEW_SUBSCRIBER.route('/token/<code>')
def token(code):
    if request.method == 'GET':
        s = Subscriber.verify_login(_type='code', code=code)
        if not s or not s.data:
            session['show_info'] = ('003', )
            session['status_code'] = 404
            return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

        session['s_login_token'] = s.make_login('token')

        return redirect(url_for('subscriber.intro', _scheme='https', _external=True))

@VIEW_SUBSCRIBER.route('/intro', methods=('GET', 'POST'))
def intro():
    if 's_login_token' not in session:
        session['show_info'] = ('003', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    user = Subscriber.verify_login(_type='token', code=session['s_login_token'])
    if not user or not user.data:
        session['show_info'] = ('003', )
        session['status_code'] = 404
        return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

    if request.method == 'GET':
        return render_template('./subscriber_intro.html')

    elif request.method == 'POST':
        post_data = request.get_json()

        if 'casename' not in post_data:
            return jsonify({}), 401

        if post_data['casename'] == 'get':
            data = {
                'name': user.data['name'],
                'mails': user.data['mails'],
                'login_since': user.login_token_data['created_at'],
                'unsubscribe': user.data['unsubscribe'],
            }
            return jsonify({'data': data})

        elif post_data['casename'] == 'update':
            data = post_data['data']

            update = {}
            update['name'] = data['name'].strip()
            update['status'] = bool(data['unsubscribe'])

            user.update_date(data=data)

            return jsonify({})

@VIEW_SUBSCRIBER.route('/clean', methods=('GET', 'POST'))
def clean():
    session.pop('s_login_token', None)

    session['show_info'] = ('004', )
    session['status_code'] = 200
    return redirect(url_for('subscriber.info_msg', _scheme='https', _external=True))

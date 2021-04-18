import logging
logging.basicConfig(
    filename='./log/log.log',
    format='%(asctime)s [%(levelname)-5.5s][%(thread)6.6s] [%(module)s:%(funcName)s#%(lineno)d]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG)

import hashlib
import os
import traceback
#import re
from urllib.parse import parse_qs
from urllib.parse import urlparse

import arrow
import google_auth_oauthlib.flow
from apiclient import discovery
from flask import Flask
from flask import g
from flask import got_request_exception
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

import setting
from celery_task.task_mail_sys import mail_sys_weberror
from view.admin_subscriber import VIEW_ADMIN_SUBSCRIBER
from view.reader import VIEW_READER
from view.subscribe import VIEW_SUBSCRIBE
from view.subscriber import VIEW_SUBSCRIBER
from view.trello import VIEW_TRELLO


app = Flask(__name__)
app.config['SESSION_COOKIE_SECURE'] = True
app.secret_key = setting.SECRET_KEY
app.register_blueprint(VIEW_ADMIN_SUBSCRIBER)
app.register_blueprint(VIEW_READER)
app.register_blueprint(VIEW_SUBSCRIBE)
app.register_blueprint(VIEW_SUBSCRIBER)
app.register_blueprint(VIEW_TRELLO)


NO_NEED_LOGIN_PATH = (
    '/',
    '/oauth2callback',
    '/logout',
    '/exception',
)

@app.before_request
def need_login():
    app.logger.info('[X-SSL-SESSION-ID: %s] [X-REAL-IP: %s] [USER-AGENT: %s] [SESSION: %s]' % (
            request.headers.get('X-SSL-SESSION-ID'),
            request.headers.get('X-REAL-IP'),
            request.headers.get('USER-AGENT'),
            session, )
       )

    if request.path not in NO_NEED_LOGIN_PATH \
            and not request.path.startswith('/subscriber') \
            and not request.path.startswith('/subscribe') \
            and not request.path.startswith('/trello') \
            and not request.path.startswith('/r/'):
        if not session.get('u'):
            session['r'] = request.path
            return redirect(url_for('oauth2logout', _scheme='https', _external=True))


@app.after_request
def no_store(response):
    ''' return no-store '''
    if session.get('u'):
        response.headers['Cache-Control'] = 'no-store'

    return response

@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/oauth2callback')
def oauth2callback():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        setting.CLIENT_SECRET,
        scopes=(
          'openid',
          'https://www.googleapis.com/auth/userinfo.email',
          'https://www.googleapis.com/auth/userinfo.profile',
        ),
        redirect_uri='https://%s/oauth2callback' % setting.DOMAIN,
    )

    if 'code' not in request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=hashlib.sha256(os.urandom(2048)).hexdigest(),
        )

        session['state'] = state
        return redirect(authorization_url)

    url = request.url.replace('http://', 'https://')
    url_query = parse_qs(urlparse(url).query)

    if 'state' in url_query and url_query['state'] and url_query['state'][0] == session.get('state'):
        flow.fetch_token(authorization_response=url)

        auth_client = discovery.build('oauth2', 'v2', credentials=flow.credentials, cache_discovery=False)
        user_info = auth_client.userinfo().get().execute()

        session['email'] = user_info['email'].lower()
        session['u'] = user_info

        if 'r' in session:
            r = session['r']
            app.logger.info('login r: %s' % r)
            session.pop('r', None)
            session.pop('state', None)
            return redirect(r)

        return redirect(url_for('index', _scheme='https', _external=True))

    else:
        session.pop('state', None)
        return redirect(url_for('oauth2callback', _scheme='https', _external=True))


@app.route('/logout')
def oauth2logout():
    ''' Logout

        **GET** ``/logout``

        :return: Remove cookie/session.
    '''
    session.pop('u', None)

    if session.get('r'):
        return redirect(url_for('oauth2callback', _scheme='https', _external=True))

    return redirect(url_for('index', _scheme='https', _external=True))

@app.route('/exception')
def exception():
    try:
        1/0
    except Exception as e:
        raise Exception('Error: [%s]' % e)

def error_exception(sender, exception, **extra):
    mail_sys_weberror.apply_async(
        kwargs={
            'title': u'%s %s %s' % (request.method, request.path, arrow.now()),
            'body': '''<b>%s</b> %s<br>
            <pre>%s</pre>
            <pre>%s</pre>
            <pre>User: %s\n\nsid: %s\n\nargs: %s\n\nform: %s\n\nvalues: %s\n\n%s</pre>''' %
            (request.method, request.path, os.environ, request.headers,
             g.get('user', {}).get('account', {}).get('_id'), session.get('sid'), request.args, request.form, request.values, traceback.format_exc())
        })

got_request_exception.connect(error_exception, app)

if __name__ == '__main__':
    app.run(debug=False, host=setting.SERVER_HOST, port=setting.SERVER_PORT)


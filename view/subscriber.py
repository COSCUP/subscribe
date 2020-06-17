from flask import Blueprint
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from module.subscriber import Subscriber

VIEW_SUBSCRIBER = Blueprint('subscriber', __name__, url_prefix='/subscriber')


@VIEW_SUBSCRIBER.route('/code/<code>', methods=('GET', 'POST'))
def code_page(code):
    if request.method == 'GET':
        return render_template('./subscriber.html')

    elif request.method == 'POST':
        s = Subscriber(mail=request.form['mail'])
        if not s.data:
            return u'', 404

        if s.verify_admin_code(code):
            code = s.make_login(_type='code')
            return u'code: %s' % code

        return jsonify({'info': 'no permission'}), 401

@VIEW_SUBSCRIBER.route('/token/<code>')
def token(code):
    if request.method == 'GET':
        s = Subscriber.verify_login(_type='code', code=code)
        if not s.data:
            return u'', 404

        session['s_login_token'] = s.make_login('token')

        return redirect(url_for('subscriber.intro', _scheme='https', _external=True))


@VIEW_SUBSCRIBER.route('/intro', methods=('GET', 'POST'))
def intro():
    if 's_login_token' not in session:
        return u'', 401

    user = Subscriber.verify_login(_type='token', code=session['s_login_token'])
    if not user.data:
        return u'', 401

    if request.method == 'GET':
        return u'hi intro %s' % user.data

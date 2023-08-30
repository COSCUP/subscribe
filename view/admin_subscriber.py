''' Admin page '''
import csv
import io
from datetime import datetime

from flask import (Blueprint, Response, jsonify, make_response,
                   render_template, request)
from werkzeug.wrappers import Response as ResponseBase

from celery_task.task_mail_sys import mail_verify_mail
from models.subscriberdb import SubscriberDB, SubscriberReadDB
from module.subscriber import GenLists, Subscriber

VIEW_ADMIN_SUBSCRIBER = Blueprint(
    'admin_subscriber', __name__, url_prefix='/admin/subscriber')


@VIEW_ADMIN_SUBSCRIBER.route('/')
def index() -> str:
    ''' index page '''
    return render_template('./admin_subscriber.html')


@VIEW_ADMIN_SUBSCRIBER.route('/add', methods=('GET', 'POST'))
def add() -> str:
    ''' add '''
    if request.method == 'GET':
        return render_template('./admin_subscriber_add.html')

    if request.method == 'POST':
        data = io.StringIO(request.files['file'].read().decode('utf-8'))
        csv_data = list(csv.DictReader(data))

        _new = 0
        for _data in csv_data:
            result = Subscriber.process_upload(
                mail=_data['mail'], name=_data['name'])
            if result:
                if result[0] == 'new':
                    _new += 1

        return f'process: {len(csv_data)}, new: {_new}'

    return ''


@VIEW_ADMIN_SUBSCRIBER.route('/list', methods=('GET', 'POST'))
def lists() -> str | ResponseBase:
    ''' lists '''
    # pylint: disable=too-many-return-statements
    if request.method == 'GET':
        return render_template('./admin_subscriber_list.html')

    if request.method == 'POST':
        post_data = request.get_json()

        if 'casename' not in post_data:
            return make_response({}, 401)

        if post_data['casename'] == 'get':
            datas = []
            for data in SubscriberDB().find():
                datas.append({
                    '_id': data['_id'],
                    'code': data['code'],
                    'ucode': data['ucode'],
                    'name': data['name'],
                    'mails': data['mails'],
                    'created_at': data['created_at'],
                    'verified_email': data['verified_email'],
                    'status': data['status'],
                    'admin_code': '',
                })
            return jsonify({'datas': datas})

        if post_data['casename'] == 'getcode':
            user = Subscriber(mail=post_data['_id'])
            return jsonify({'code': user.render_admin_code()})

        if post_data['casename'] == 'changestatus':
            user = Subscriber(mail=post_data['_id'])
            user.update_date({'status': post_data['status']})

            return jsonify({'data': post_data})

        if post_data['casename'] == 'sendverify':
            mail_verify_mail.apply_async(kwargs={'mail': post_data['_id']})
            return jsonify({})

    return ''


@VIEW_ADMIN_SUBSCRIBER.route('/list/dl')
def download() -> ResponseBase:
    ''' name, mails[-1] '''
    with io.StringIO() as files:
        fieldnames = ('name', 'mail', 'status', 'verified_email',
                      'admin_link', 'ucode', 'args', 'openhash')
        csv_writer = csv.DictWriter(
            files, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()

        for row in GenLists.dumps(request_args=request.args):
            csv_writer.writerow(row)  # type:ignore

        filename = f"coscup_paper_subscribers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            files.getvalue(),
            mimetype='text/csv',
            headers={'Content-disposition': f'attachment; filename={filename}',
                     'x-filename': filename,
                     })


@VIEW_ADMIN_SUBSCRIBER.route('/open', methods=('GET', 'POST'))
def open_rate() -> str | ResponseBase:
    ''' Open rate '''
    if request.method == 'GET':
        return render_template('./admin_subscriber_open.html')
    if request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'topics':
            topics = SubscriberReadDB().distinct('topic')

            return jsonify({'topics': topics})

        if post_data['casename'] == 'get':
            datas = []
            for raw in SubscriberReadDB().find(
                {'topic': post_data['topic']},
                sort=(('created_at', -1), ),
            ):
                datas.append({
                    '_id': str(raw['_id']),
                    'created_at': raw['created_at'],
                    'ucode': raw['ucode'],
                    'headers': {'User-Agent': raw['headers']['User-Agent'],
                                'X-Real-Ip': raw['headers']['X-Real-Ip'], },
                })

            return jsonify({'datas': datas})

        return jsonify({})
    return ''

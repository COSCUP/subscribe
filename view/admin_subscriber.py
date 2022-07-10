import csv
import io
from datetime import datetime

from flask import Blueprint, Response, jsonify, render_template, request

from celery_task.task_mail_sys import mail_verify_mail
from models.subscriberdb import SubscriberDB, SubscriberReadDB
from module.subscriber import GenLists, Subscriber
from module.utils import hmac_encode

VIEW_ADMIN_SUBSCRIBER = Blueprint(
    'admin_subscriber', __name__, url_prefix='/admin/subscriber')


@VIEW_ADMIN_SUBSCRIBER.route('/')
def index():
    return render_template('./admin_subscriber.html')


@VIEW_ADMIN_SUBSCRIBER.route('/add', methods=('GET', 'POST'))
def add():
    if request.method == 'GET':
        return render_template('./admin_subscriber_add.html')

    elif request.method == 'POST':
        data = io.StringIO(request.files['file'].read().decode('utf-8'))
        csv_data = list(csv.DictReader(data))

        _new = 0
        for data in csv_data:
            _type, uni_mail = Subscriber.process_upload(
                mail=data['mail'], name=data['name'])
            if _type == 'new':
                _new += 1

        return u'process: %s, new: %s' % (len(csv_data), _new)


@VIEW_ADMIN_SUBSCRIBER.route('/list', methods=('GET', 'POST'))
def lists():
    if request.method == 'GET':
        return render_template('./admin_subscriber_list.html')

    elif request.method == 'POST':
        post_data = request.get_json()

        if 'casename' not in post_data:
            return u'', 401

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

        elif post_data['casename'] == 'getcode':
            user = Subscriber(mail=post_data['_id'])
            return jsonify({'code': user.render_admin_code()})

        elif post_data['casename'] == 'changestatus':
            user = Subscriber(mail=post_data['_id'])
            user.update_date({'status': post_data['status']})

            return jsonify({'data': post_data})

        elif post_data['casename'] == 'sendverify':
            mail_verify_mail.apply_async(kwargs={'mail': post_data['_id']})
            return jsonify({})


@VIEW_ADMIN_SUBSCRIBER.route('/list/dl')
def dl():
    ''' name, mails[-1] '''
    with io.StringIO() as files:
        fieldnames = ('name', 'mail', 'status', 'verified_email',
                      'admin_link', 'ucode', 'args', 'openhash')
        csv_writer = csv.DictWriter(
            files, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writeheader()

        for row in GenLists.dumps(request_args=request.args):
            csv_writer.writerow(row)

        filename = 'coscup_paper_subscribers_%s.csv' % datetime.now().strftime('%Y%m%d_%H%M%S')

        return Response(
            files.getvalue(),
            mimetype='text/csv',
            headers={'Content-disposition': 'attachment; filename=%s' % filename,
                     'x-filename': filename,
                     })


@VIEW_ADMIN_SUBSCRIBER.route('/open', methods=('GET', 'POST'))
def open_rate():
    if request.method == 'GET':
        return render_template('./admin_subscriber_open.html')
    elif request.method == 'POST':
        post_data = request.get_json()

        if post_data['casename'] == 'topics':
            topics = SubscriberReadDB().distinct('topic')

            return jsonify({'topics': topics})

        elif post_data['casename'] == 'get':
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

import csv
import io

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request

from models.subscriberdb import SubscriberDB
from module.subscriber import Subscriber

VIEW_ADMIN_SUBSCRIBER = Blueprint('admin_subscriber', __name__, url_prefix='/admin/subscriber')


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

        for data in csv_data:
            Subscriber.process_upload(mail=data['mail'], name=data['name'])

        return u'add: %s' % len(csv_data)

@VIEW_ADMIN_SUBSCRIBER.route('/list', methods=('GET', 'POST'))
def lists():
    if request.method == 'GET':
        return render_template('./admin_subscriber_list.html')

    elif request.method == 'POST':
        post_data = request.get_json()

        if 'casename' in post_data and post_data['casename'] == 'get':
            datas = []
            for sub in SubscriberDB().find({}, {'_id': 1}):
                sub = Subscriber(mail=sub['_id'])
                datas.append({
                    '_id': sub.data['_id'],
                    'code': sub.data['code'],
                    'name': sub.data['name'],
                    'mails': sub.data['mails'],
                    'created_at': sub.data['created_at'],
                    'admin_code': sub.render_admin_code(),
                })
            return jsonify({'datas': datas})

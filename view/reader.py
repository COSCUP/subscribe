import logging

from flask import Blueprint
from flask import request

from models.subscriberdb import SubscriberDB
from module.subscriber import SubscriberRead
from module.utils import hmac_encode
from module.utils import hmac_verify

VIEW_READER = Blueprint('reader', __name__, url_prefix='/r')

@VIEW_READER.route('/')
def index():
    return u'hi'

@VIEW_READER.route('/<ucode>/<hash_str>')
def read_page(ucode, hash_str):
    logging.info(dict(request.headers))
    query = request.query_string.decode('utf8')
    if not query:
        return u'', 404

    user = SubscriberDB().find_one({'ucode': ucode}, {'code': 1})
    if user and hmac_verify(code=user['code'], hash_str=hash_str, args_str=query):
        if 't' not in request.args or not request.args['t']:
            return u'', 404

        SubscriberRead.add(
                ucode=ucode,
                topic=request.args['t'],
                headers=request.headers,
                args=query,
            )

    return u'', 404

'''
api: https://developer.atlassian.com/cloud/trello/guides/rest-api/webhooks/

'''
import json
import logging

import requests
from flask import Blueprint
from flask import request

import setting

VIEW_TRELLO = Blueprint('trello', __name__, url_prefix='/trello')


@VIEW_TRELLO.route('/', methods=('POST', 'GET', 'HEAD'))
def index():
    if request.method in ('GET', 'HEAD'):
        return 'hi'

    data = request.get_json()
    logging.info('trello: %s, %s', data, type(data))

    wording = ''
    if 'action' in data:
        if 'type' in data['action'] and data['action']['type'] == 'commentCard':
            _action = data['action']
            wording = '**%s** 在 **[%s](%s)** 留言說明：\n%s' % (
                    _action['display']['entities']['memberCreator']['text'],
                    _action['data']['card']['name'],
                    'https://trello.com/c/%s/%s' % (_action['data']['card']['shortLink'], _action['data']['card']['idShort']),
                    _action['data']['text'],
            )

        if 'type' in data['action'] and data['action']['type'] == 'createCard':
            _action = data['action']
            wording = '**%s** 新增一張卡片 **[%s](%s)** (%s)' % (
                    _action['display']['entities']['memberCreator']['text'],
                    _action['data']['card']['name'],
                    'https://trello.com/c/%s/%s' % (_action['data']['card']['shortLink'], _action['data']['card']['idShort']),
                    '列表： **_%s_**' % _action['data']['list']['name'],
            )

        if 'type' in data['action'] and data['action']['type'] == 'updateCard':
            _action = data['action']
            if 'old' in _action['data'] and 'name' in _action['data']['old']:
                wording = '**%s** 變更卡片名稱 **_%s_** -> **_[%s](%s)_**' % (
                        _action['display']['entities']['memberCreator']['text'],
                        _action['data']['old']['name'],
                        _action['data']['card']['name'],
                        'https://trello.com/c/%s/%s' % (_action['data']['card']['shortLink'], _action['data']['card']['idShort']),
                )

            if 'old' in _action['data'] and 'desc' in _action['data']['old']:
                wording = '**%s** 調整了 **[%s](%s)** 卡片內容。' % (
                        _action['display']['entities']['memberCreator']['text'],
                        _action['data']['card']['name'],
                        'https://trello.com/c/%s/%s' % (_action['data']['card']['shortLink'], _action['data']['card']['idShort']),
                )

            if 'old' in _action['data'] and 'idList' in _action['data']['old']:
                wording = '**%s** 移動 **[%s](%s)** 卡片 **_%s_** -> **_%s_**' % (
                        _action['display']['entities']['memberCreator']['text'],
                        _action['data']['card']['name'],
                        'https://trello.com/c/%s/%s' % (_action['data']['card']['shortLink'], _action['data']['card']['idShort']),
                        _action['data']['listBefore']['name'],
                        _action['data']['listAfter']['name'],
                )

    if wording:
        logging.info('trello wording: %s', wording)

        requests.post(
                setting.TRELLO_HOOK,
                json={'text': wording, 'props': {'card': '```\n%s\n```' % _action}})

    return ''


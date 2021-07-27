from datetime import datetime
from requests.sessions import Session


class GaConn(Session):
    ''' Ga Conn '''
    def __init__(self, measurement_id, api_secret):
        self.measurement_id = measurement_id
        self.api_secret = api_secret
        self.url = 'https://www.google-analytics.com/mp/collect'

        super(GaConn, self).__init__()
        self.params = {
                'measurement_id': self.measurement_id,
                'api_secret': self.api_secret,
            }

    def post(self, path, *args, **kwargs):
        ''' POST '''
        return super(GaConn, self).post(self.url + path, *args, **kwargs)

    def event_mail_open(self, ucode, topic, timestamp_micros=None):
        ''' Event mail_open '''
        if timestamp_micros is None:
            timestamp_micros = int(datetime.now().timestamp()*1000000)

        data = {
                'client_id': ucode,
                'user_id': ucode,
                'timestamp_micros': timestamp_micros,
                'non_personalized_ads': False,
                'events': [{
                        'name': 'mail_open',
                        'params': {
                            'uid': ucode,
                            'topic': topic,
                        }
                    }],
            }

        self.post(path='', json=data)

    def event_mail_subscribe(self, ucode, timestamp_micros=None):
        ''' Event mail_subscribe '''
        if timestamp_micros is None:
            timestamp_micros = int(datetime.now().timestamp()*1000000)

        data = {
                'client_id': ucode,
                'user_id': ucode,
                'timestamp_micros': timestamp_micros,
                'non_personalized_ads': False,
                'events': [{
                        'name': 'mail_subscribe',
                        'params': {
                            'uid': ucode,
                        }
                    }],
            }

        self.post(path='', json=data)


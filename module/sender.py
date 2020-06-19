import jinja2

import setting
from module.awsses import AWSSES


class SenderMailer(object):
    ''' Sender Mailer
    :param str template_path: template path
    :param str subject: subject
    :param dict source: {'name': str, 'mail': str}
    '''
    def __init__(self, template_path, subject, content, source=None):
        body = jinja2.Environment().from_string(open(template_path, 'r').read()).render(**content)

        self.tpl = jinja2.Environment().from_string(body)
        self.subject = jinja2.Environment().from_string(subject)

        if source is None:
            source = setting.AWS_SES_FROM

        self.awsses = AWSSES(aws_access_key_id=setting.AWS_ID,
                aws_secret_access_key=setting.AWS_KEY, source=source)

    def send(self, to_list, data, x_coscup=None):
        ''' Send mail
        :param list to_list: [{'name': str, 'mail': str}, ]
        :param dict data: data for render
        '''
        raw_mail = self.awsses.raw_mail(
            to_addresses=to_list,
            subject=self.subject.render(**data),
            body=self.tpl.render(**data),
            x_coscup=x_coscup,
        )
        return self.awsses.send_raw_email(data=raw_mail)


class SenderMailerCOSCUP(SenderMailer):
    ''' Sender using COSCUP template '''
    def __init__(self, subject, content, source=None):
        super(SenderMailerCOSCUP, self).__init__(
            template_path='/app/templates/mail/coscup_base.html',
            subject=subject, content=content, source=source)


class SenderMailerSubscribeLoginCode(SenderMailer):
    ''' Sender for subscriber login code '''
    def __init__(self, subject, content, source=None):
        super(SenderMailerSubscribeLoginCode, self).__init__(
            template_path='/app/templates/mail/coscup_subscribe_login_code.html',
            subject=subject, content=content, source=source)


class SenderMailerSubscribeVerify(SenderMailer):
    ''' Sender for subscriber verify mail '''
    def __init__(self, subject, content, source=None):
        super(SenderMailerSubscribeVerify, self).__init__(
            template_path='/app/templates/mail/coscup_subscribe_verify_mail.html',
            subject=subject, content=content, source=source)

import os
import sys
import email
import notmuch
import subprocess

from bottle import route, run, response

from utils import extract_body

db = notmuch.Database('/home/tosh/mail')
MAX_RESULTS = 100


class Message(object):
    def __init__(self, message):
        self.message = message
        self._email = None

    @property
    def date(self):
        return self.message.get_header('date')

    @property
    def subject(self):
        return self.message.get_header('subject')

    @property
    def author(self):
        return self.message.get_header('from')

    @property
    def tags(self):
        return [x for x in self.message.get_tags()]

    @property
    def message_id(self):
        return self.message.get_message_id()

    @property
    def get_email(self):
        path = self.message.get_filename()
        warning = "Subject: Caution!\n"\
                  "Message file is no longer accessible:\n%s" % path
        if not self._email:
            try:
                with open(path) as f:
                    self._email = email.message_from_file(f)
            except IOError:
                self._email = email.message_from_string(warning)
        return extract_body(self._email)

    @property
    def as_dict(self):
        # TODO don't include body in every message by default
        # should only be parsed for message view not lists
        return {
            'message_id': self.message_id,
            'date': self.date,
            'subject': self.subject,
            'tags': self.tags,
            'author': self.author,
            'body': '{}'.format(self.get_email)
        }


class Thread(object):
    def __init__(self, thread):
        self.thread = thread

    @property
    def thread_id(self):
        return self.thread.get_thread_id()

    @property
    def subject(self):
        return self.thread.get_subject()

    @property
    def tags(self):
        return [x for x in self.thread.get_tags()]

    @property
    def authors(self):
        return self.thread.get_authors()

    @property
    def date(self):
        import datetime
        dtime = datetime.datetime.fromtimestamp(self.thread.get_newest_date())
        return dtime.isoformat()

    @property
    def as_dict(self):
        return {
            'thread_id': self.thread_id,
            'date': self.date,
            'subject': self.subject,
            'tags': self.tags,
            'authors': self.authors
        }


@route('/api/threads/<tag>')
def threads(tag):
    print('--------')
    print(tag)
    query = db.create_query('{}'.format(tag))
    threads = [Thread(x).as_dict for x in islice(query.search_threads(), MAX_RESULTS)]
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'application/json'
    res = {'total': query.count_threads(), 'threads': threads}
    return res

import json
from itertools import islice
@route('/api/messages/<tag>')
def messages(tag):
    print('--------')
    print(tag)
    query = db.create_query('{}'.format(tag))
    messages = [Message(x).as_dict for x in islice(query.search_messages(), MAX_RESULTS)]
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'application/json'
    res = {'total': query.count_messages(), 'messages': messages}
    return res

@route('/api/thread/<id>')
def thread(id):
    print('------')
    print(id)
    query = db.create_query('thread:{}'.format(id))
    messages = [Message(x).as_dict for x in islice(query.search_messages(), MAX_RESULTS)]
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'application/json'
    res = {'total': query.count_messages(), 'messages': messages}
    return res

@route('/api/reply/<message_id>')
def reply(message_id):
    command = ['emacsclient', '--eval', '(require \'notmuch-mua)', '--eval', '(require \'notmuch-show)', '--eval', '(notmuch-mua-new-reply \"id:{message_id}\")'.format(message_id=message_id)
]
    #command = "emacsclient --eval '(require \'notmuch-mua)' --eval '(require \'notmuch-show)' --eval '(notmuch-mua-new-reply \"id:{message_id}\")'".format(message_id=message_id)
    response = subprocess.check_output(command)
    print(response)
    return {"status": 200, "response": ''}

@route('/api/server/restart')
def restart_server():
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == '__main__':
    run(host='localhost', port=8080, reloader=True)

# notes and stuff

# launch emacs to send reply to message_id
# emacsclient --eval '(require \'notmuch-mua)' --eval '(require \'notmuch-show)' --eval '(notmuch-mua-new-reply "id:20180111040201.10339.90785@sentry02.ams1.uniregistrar.net")'

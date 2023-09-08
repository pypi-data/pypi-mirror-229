import os.path
import tempfile
import unittest

import requests
from wsgiadapter import WSGIAdapter  # from requests-wsgi-adapter

from drakken.core import Drakken
import drakken.model as model
from drakken.template import render
from drakken.config import loads


class TestCSRFToken(unittest.TestCase):
    def setUp(self):
        cfg = {
            'DATABASE_URL': 'sqlite:///:memory:',
            'TEMPLATE_DIR': '',
        }
        loads(cfg)

        model.setup()
        self.email = 'stuart@erewhon.com'
        self.password = 'Found in the swamp'
        model.create_user(self.email, self.password)

        self.app = Drakken()
        self.client = requests.Session()
        self.client.mount(
            prefix='http://testserver',
            adapter=WSGIAdapter(
                self.app))

        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, 'test.html')

    def test_no_CSRF_in_template(self):
        html = '<html><p>Hello</p></html>'
        with open(self.path, 'w') as f:
            f.write(html)

        @self.app.route('/hello')
        def hello(request, response):
            response.text = render(request, self.path)

        user_agent = self.client.headers['User-Agent']
        headers = {'user-agent': user_agent}
        r = self.client.get(
            'http://testserver/hello',
            headers=headers)
        self.assertTrue('<p>Hello</p>' in r.text)

        with model.session_scope() as sql_session:
            count = sql_session.query(model.Session).count()
            self.assertEqual(count, 0)

    def test_not_logged_in(self):
        html = '<html>${CSRF}</html>'
        with open(self.path, 'w') as f:
            f.write(html)

        @ self.app.route('/create-account')
        def create_account(request, response):
            response.text = render(request, self.path)

        user_agent = self.client.headers['User-Agent']
        headers = {'user-agent': user_agent}
        r = self.client.get(
            'http://testserver/create-account',
            headers=headers)

        with model.session_scope() as sql_session:
            token = sql_session.query(model.Session).first().csrf_token
            self.assertTrue(token in r.text)

    def tearDown(self):
        self.dir.cleanup()


class TestNoDB(unittest.TestCase):
    # Can use Drakken without a database.
    def setUp(self):
        cfg = {
            # We don't call model.setup() so the URL can be anything.
            'DATABASE_URL': None,
            'TEMPLATE_DIR': '',
        }
        loads(cfg)
        # Don't call model.setup()
        self.app = Drakken()
        self.client = requests.Session()
        self.client.mount(
            prefix='http://testserver',
            adapter=WSGIAdapter(
                self.app))

        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, 'test.html')

    def test_html(self):
        html = '<html><p>Hello</p></html>'
        with open(self.path, 'w') as f:
            f.write(html)

        @self.app.route('/hello')
        def hello(request, response):
            response.text = render(request, self.path)

        r = self.client.get(
            'http://testserver/hello')
        self.assertTrue('<p>Hello</p>' in r.text)

    def tearDown(self):
        self.dir.cleanup()


if __name__ == '__main__':
    unittest.main()


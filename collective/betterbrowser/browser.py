import thread
import time
import webbrowser
import cgi
import urllib
import plone.testing.z2

try:
    from pyquery import PyQuery
    PYQUERY_AVAILABLE = True
except:
    PYQUERY_AVAILABLE = False


from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


def new_browser(layer):

    assert layer, """
        No layer given.
    """

    assert 'app' in layer, """
        No app set up on layer
    """

    assert 'portal' in layer, """
        No portal set up on layer
    """

    browser = BetterBrowser(layer['app'])
    browser.portal = layer['portal']
    browser.handleErrors = False

    def raising(self, info):
        import traceback
        traceback.print_tb(info[2])
        print info[1]

    from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
    SiteErrorLog.raising = raising

    return browser


class BetterBrowser(plone.testing.z2.Browser):

    portal = None

    @property
    def baseurl(self):
        return self.portal.absolute_url()

    def open(self, url, data=None):
        if url.startswith('/'):
            url = self.baseurl + url
        super(self.__class__, self).open(url, data)

    def login(self, user, password):
        self.open('/login_form')
        self.getControl(name='__ac_name').value = user
        self.getControl(name='__ac_password').value = password
        self.getControl(name='submit').click()

        assert 'logout' in self.contents

    def logout(self):
        self.open('/logout')

        assert 'logged out' in self.contents

    def login_admin(self):
        self.login('admin', 'secret')

    def login_testuser(self):
        self.login('test-user', 'secret')

    def assert_http_exception(self, url, exception):
        self.portal.error_log._ignored_exceptions = ()
        self.portal.acl_users.credentials_cookie_auth.login_path = ""

        expected = False
        try:
            self.open(url)
        except Exception, e:

            # zope does not always raise unathorized exceptions with the
            # correct class signature, so we need to do this thing:
            expected = e.__repr__().startswith(exception)

            if not expected:
                raise

        assert expected

    def assert_unauthorized(self, url):
        self.assert_http_exception(url, 'Unauthorized')

    def assert_notfound(self, url):
        self.assert_http_exception(url, 'NotFound')

    def query(self, selector):
        assert PYQUERY_AVAILABLE, """
            to use, install collective.betterbrowser with pyquery, e.g:
            collective.betterbrowser[pyquery]
        """

        # there's probably better performance to be had by caching this
        return PyQuery(self.contents)(selector)

    def assert_count(self, query, count):
        assert len(self.query(query)) == count

    def assert_present(self, query):
        self.assert_count(query, 1)

    def assert_missing(self, query):
        self.assert_count(query, 0)

    def show(self, port=8888, open_in_browser=True, threaded=False):
        """ Serves the currently open site on localhost:<port> handling all
        requests for full browser support.

        During the session the browser will open other sites. The old one is
        reset after the server is killed using ctrl+c

        """

        browser = self

        external_base_url = 'http://localhost:{}/'.format(port)
        internal_base_url = 'http://nohost/'

        # stitch the local variables to the GetHandler class when it is created
        def handler_factory(*args, **kwargs):
            instance = type(*args, **kwargs)
            instance.internal_base_url = internal_base_url
            instance.external_base_url = external_base_url
            instance.browser = browser
            return instance

        class RequestHandler(BaseHTTPRequestHandler, object):

            __metaclass__ = handler_factory

            @property
            def internal_url(self):
                return self.internal_base_url + self.path

            def reencode_post_data(self):
                """ Parse the post data and urlencode them again. This ensures
                that the browser knows what to do with the data. It doesn't
                seem to be too flexible there.

                """
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type')
                )

                if ctype == 'multipart/form-data':
                    parsed = cgi.parse_multipart(self.rfile, pdict)

                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    parsed = cgi.parse_qs(
                        self.rfile.read(length), keep_blank_values=1
                    )

                else:
                    parsed = {}

                return urllib.urlencode(parsed, True)

            def externalize(self, body):
                return body.replace(
                    self.internal_base_url, self.external_base_url
                )

            def do_GET(self):
                self.browser.open(self.internal_url)
                self.respond()

            def do_POST(self):

                data = self.reencode_post_data()

                self.browser.open(self.internal_url, data)
                self.respond()

            def respond(self):
                """ Write the current browser's content into the response. """

                self.send_response(int(self.browser.headers['status'][:3]))

                # adjust the headers except for the content-length which might
                # later differ because the body may change
                for key, header in self.browser.headers.items():
                    if key != 'content-length':
                        self.send_header(key, header)

                body = self.externalize(self.browser.contents)

                # calculate the length and send
                self.send_header('Content-Length', len(body))
                self.end_headers()

                self.wfile.write(body)

        open_url = browser.url

        # open the external bseurl in an external browser with a short delay
        # to get the TCPServer time to start listening
        if open_in_browser:
            def open_browser(url):
                time.sleep(0.5)
                webbrowser.open(url)

            url = browser.url.replace(internal_base_url, external_base_url)
            thread.start_new_thread(open_browser, (url, ))

        server = HTTPServer(('localhost', port), RequestHandler)

        if not threaded:
            try:
                # continue until the user presses ctril+c in the console
                server.serve_forever()
            except KeyboardInterrupt:
                pass

            # reopen the last used url
            browser.open(open_url)
        else:
            # start the server and return a close function
            thread.start_new_thread(server.serve_forever, ())

            def close():
                server.shutdown()
                browser.open(open_url)

            return close

    def set_date(self, widget, date):
        self.getControl(name='%s-year' % widget).value = str(date.year)
        self.getControl(name='%s-month' % widget).value = [str(date.month)]
        self.getControl(name='%s-day' % widget).value = str(date.day)
        self.getControl(name='%s-hour' % widget).value = str(date.hour)
        self.getControl(name='%s-minute' % widget).value = str(date.minute)

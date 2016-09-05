import webapp2


class RequestHandler(webapp2.RequestHandler):
    def options(self):
        self.response.headers.add('Access-Control-Allow-Origin', '*')
        self.response.headers.add('Access-Control-Allow-Headers', 'Content-Type')

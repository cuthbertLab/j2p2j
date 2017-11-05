import tornado.web

class IndexHandler(tornado.web.RequestHandler):
    def initialize(self, options=None):
        self.options = options
        if (options is not None and 'htmlStart' in options):
            self.htmlStart = options['htmlStart']
        else:
            self.htmlStart = 'index.html'

        if (options is not None and 'j2p2j' in options):
            self.j2p2j = options['j2p2j']

    @tornado.web.asynchronous
    def get(self, **kwargs):
        #self.write("This is your response")
        #if "Id" in kwargs.keys():
        #    print("Your client id is: %s" % (kwargs["Id"],))
        self.render(self.htmlStart,
                    j2p2jHead=self.j2p2j.j2p2jHead)
        #self.finish()

class IndexAwareStaticFileHandler(tornado.web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return super().parse_url_path(url_path)

import tornado.ioloop
import tornado.web
import tornado.gen

import rons
client = rons.Client()

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.write(" [*] Waiting....")
        self.flush()
        r = yield tornado.gen.Task( self.client.subscribe, 'test' )
        self.write(r)
        print r
        self.finish()


application = tornado.web.Application([
    (r"/", MainHandler),
])


if __name__ == "__main__":
    print " [*] Listening on http://localhost:8888/"
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

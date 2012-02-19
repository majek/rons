RonS
====

A simplistic, asynchronous Redis client for [Python Tornado](http://www.tornadoweb.org).

Currently supports only SUBSCRIBE method (UNSUBSCRIBE is implicit).


Usage:

```python
import rons
client = rons.Client()

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.engine
    @rons.save_generator
    def get(self):
        self.set_header('Content-Type', 'text/plain')
        self.write(" [*] Waiting....\n")
        self.flush()
        r = yield tornado.gen.Task( client.subscribe, 'test' )
        self.write(" [!] Got %r\n" % (r,))
        self.flush()
        self.finish()

    def on_connection_close(self):
        rons.stop_generator(self)

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    print " [*] Listening on http://localhost:8888/"
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

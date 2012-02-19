import collections
import socket
import tornado.iostream

from . import parser
from . import parse_url
from . import simplebuffer

class _Connection(object):
    def _connect(self, io_loop):
        self.recv_buf = simplebuffer.SimpleBuffer()
        self.state = parser.initial_state()

        try:
            addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET, socket.SOCK_STREAM)
        except socket.gaierror:
            addrinfo = socket.getaddrinfo(self.host, self.port, socket.AF_INET6, socket.SOCK_STREAM)
        (family, socktype, proto, canonname, sockaddr) = addrinfo[0]
        self.sd = socket.socket(family, socktype, proto)
        self.stream = tornado.iostream.IOStream(self.sd, io_loop=io_loop)
        self.stream.connect(sockaddr, self.on_connect)
        self.stream.read_until_close(callback=self.on_read,
                                     streaming_callback=self.on_read)

    def on_read(self, data):
        self.recv_buf.write(data)

        pos, buf = 0, self.recv_buf.read()
        while True:
            (consumed, frame, self.state) = \
                parser.decode(buf[pos:], self.state)
            if frame:
                self.on_frame(frame)
            elif not consumed:
                break
            pos += consumed
        self.recv_buf.consume(pos)

    def write(self, *args):
        self.stream.write(parser.encode(args))


class Client(_Connection):
    def __init__(self, redis_url='redis://127.0.0.1', io_loop=None):
        (self.host, self.port, self.password, self.selected_db) = \
            parse_url.parse_redis_url(redis_url)

        self._connect(io_loop)
        self.subscriptions = collections.defaultdict( list )
        self.unsubscribes = {}
        self.connected = False

    def on_connect(self):
        if self.password:
            self.write('AUTH', self.password)
        if self.selected_db:
            self.write('SELECT', self.selected_db)
        self.connected = True
        for topic in self.subscriptions:
            self.do_subscribe( topic )


    def subscribe(self, topic, callback=None):
        subs = self.subscriptions[ topic ]
        subs.append( callback )
        if len(subs) is 1:
            if topic in self.unsubscribes:
                del self.unsubscribes[topic]
            else:
                if self.connected is True:
                    self.do_subscribe(topic)

    def do_subscribe(self, topic):
        #print 'subs ' + repr(topic)
        self.write('SUBSCRIBE', topic)

    def on_frame(self, frame):
        if frame[0] is '*':
            args = [v for (t, v) in frame[1]]
            if args[0] == 'subscribe':
                return
            elif args[0] == 'unsubscribe':
                return
            elif args[0] == 'message':
                # process msg
                assert len(args) is 3
                topic, msg = args[1], args[2]
                active_subscription = topic not in self.unsubscribes

                # cleanup old subscriptions
                for t in self.unsubscribes:
                    #print 'unsubs ' + repr(t)
                    self.write('UNSUBSCRIBE', t)
                self.unsubscribes.clear()

                if active_subscription:
                    subscriptions = self.subscriptions[topic]
                    del self.subscriptions[topic]
                    self.unsubscribes[topic] = True
                    for callback in subscriptions:
                        callback(msg)
            else:
                assert False, repr(args)
        else:
            assert frame[0] is '+', repr(frame)

import socket
import tornado.ioloop
import tornado.iostream

import rons

client = rons.Client()

def on_test(data):
    print 'test got ' + data
    client.subscribe('test', callback=on_test)
client.subscribe('test', callback=on_test)

def on_test1(data):
    print 'test1'
client.subscribe('test1', callback=on_test1)
def on_test2(data):
    print 'test2'
client.subscribe('test2', callback=on_test2)

def on_close(data):
    print data
    tornado.ioloop.IOLoop.instance().stop()

client.subscribe('close', callback=on_close)

print " [*] waiting on redis test and close channels"
tornado.ioloop.IOLoop.instance().start()

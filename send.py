import redis
import sys
r = redis.StrictRedis(host='localhost', port=6379)

topic = sys.argv[1]
data =  ' '.join(sys.argv[2:]) or 'Hello World!'
print " topic:%r data:%r" % (topic, data)
r.publish(topic, data)

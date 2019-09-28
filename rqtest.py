import requests
from rq import Queue
from redis import Redis
import time

from worker import count_words_at_url

redis_conn = Redis()
q = Queue(connection=redis_conn)

job = q.enqueue(count_words_at_url, 'http://nvie.com')
print(job.result)

time.sleep(2)

print(job.result)

breakpoint()

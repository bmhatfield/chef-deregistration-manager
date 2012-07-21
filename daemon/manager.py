import clientqueue.queue

q = clientqueue.queue.SQSQueue('chef-client-deregistration-queue-arctic', 'ACCESS_KEY', 'SECRET_KEY')

q.enqueue("test message")

print q.dequeue()
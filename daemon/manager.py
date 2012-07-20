import clientqueue.queue

q = clientqueue.queue.SQSQueue('chef-client-deregistration-queue-arctic', 'AKIAIU5C2XWX3COAUK3A', '29zbMV3uzNMsa5eoH+8JEI08EuFoXpUkX16+QIhO')

q.enqueue("test message")

print q.dequeue()
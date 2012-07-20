import boto.sqs.connection, boto.sqs.message

class SQSQueue():
    def __init__(self, queue_name, access_key, secret_key):
        self.connection = boto.sqs.connection.SQSConnection(access_key, secret_key)
        self.queue = self.connection.get_queue(queue_name)

        if self.queue is None:
            self.queue = self.connection.create_queue(queue_name)

    def enqueue(self, message):
        m = boto.sqs.message.RawMessage()
        m.set_body(message)
        
        self.queue.write(m)

    def dequeue(self):
        m = self.queue.read()

        return(m.get_body())


class Queue(SQSQueue):
    pass

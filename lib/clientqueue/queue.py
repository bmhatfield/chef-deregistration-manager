import logging
import boto.sqs.connection
import boto.sqs.message


class Queue():
    """
    Base Queue class that defines the generic queue management interface.
    """
    def enqueue(self):
        raise NotImplementedError

    def dequeue(self):
        raise NotImplementedError

    def __len__(self):
        raise NotImplementedError


class SQSQueue(Queue):
    """
    Provides a generic queue management interface wrapper around Amazon's SQS.

    For more information, please see:
    http://docs.amazonwebservices.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/Welcome.html
    http://boto.s3.amazonaws.com/sqs_tut.html
    """

    def __init__(self, queue_name, access_key, secret_key):
        self.connection = boto.sqs.connection.SQSConnection(access_key, secret_key)
        self.queue = self.connection.get_queue(queue_name)

        if self.queue is None:
            logging.info("Creating queue: %s", queue_name)
            self.queue = self.connection.create_queue(queue_name)

        self.queue.set_message_class(boto.sqs.message.RawMessage)

    def enqueue(self, message):
        m = boto.sqs.message.RawMessage()
        m.set_body(message)

        self.queue.write(m)

    def dequeue(self):
        m = self.queue.read()

        if m is not None:
            self.queue.delete_message(m)
            return(m.get_body())
        else:
            return("")

    def __len__(self):
        return(self.queue.count())

import json
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
        self.name = queue_name
        self.sqs = boto.sqs.connection.SQSConnection(access_key, secret_key)
        self.queue = self.sqs.get_queue(queue_name)

        if self.queue is None:
            logging.info("Creating queue: %s", queue_name)
            self.queue = self.sqs.create_queue(queue_name)

        self.queue_arn = self.queue.get_attributes()['QueueArn']
        self.queue.set_message_class(boto.sqs.message.RawMessage)

    def enqueue(self, message):
        m = boto.sqs.message.RawMessage()
        m.set_body(message)

        self.queue.write(m)

    def dequeue(self):
        m = self.queue.read()

        if m is not None:
            message_body = m.get_body()
            if len(message_body) > 0:
                self.queue.delete_message(m)
                return(message_body)

        return False

    def __len__(self):
        return(self.queue.count())


class AutoscalingQueue(SQSQueue):
    """
    This class should override the __init__ method of the SQSQueue class.
    The purpose of overriding the init method is to additionally set up SNS topics,
    then link the queue and the topic together.

    Creates SNS Topic with name like DC
    Creates SQS Queue with name like DC
    Adds SQS Queue as subscriber to SNS Topic with SQS Queue's ARN
    Adds SQS Permissions to SQS Queue with SNS's ARN
    """
    def __init__(self, queue_name, access_key, secret_key):
        SQSQueue.__init__(self, queue_name, access_key, secret_key)
        self.sns = boto.sns.SNSConnection(access_key, secret_key)

        self.topic = self.sns.create_topic(queue_name)
        self.topic_arn = self.topic['CreateTopicResponse']['CreateTopicResult']['TopicArn']

        s = self.sns.get_all_subscriptions_by_topic(self.topic_arn)
        self.subscriptions = [sub['Endpoint'] for sub in s['ListSubscriptionsByTopicResponse']['ListSubscriptionsByTopicResult']['Subscriptions']]

        # The below crazy list comprehension is similar to doing the following:
        # for statement in policy['Statement']:
        #     for condition in statement['Condition']:
        #         list.append(statement['Condition'][condition]['aws:SourceArn'])
        p = json.loads(self.queue.get_attributes('Policy')['Policy'])
        self.permitted_topics = [s['Condition'][d]['aws:SourceArn'] for d in [c for s in p['Statement'] for c in s['Condition']]]

        if self.topic_arn not in self.permitted_topics:
            logging.warning("Topic ARN %s not permitted to write to queue (%s)", self.topic_arn, self.name)
            logging.warning("Flushing all existing policies on %s", self.name)
            self.queue.set_attribute('Policy', '')

            logging.info("Subscribing queue (%s) to topic (%s)", self.name, self.topic_arn)
            self.sns.subscribe_sqs_queue(self.topic_arn, self.queue)
        else:
            logging.debug("Topic ARN (%s) permitted against SQS queue (%s)", self.topic_arn, self.name)
            if self.queue_arn not in self.subscriptions:
                logging.warning("%s is not subscribed to %s", self.name, self.topic_arn)
                logging.info("Subscribing %s to %s", self.name, self.topic_arn)
                self.sns.subscribe(self.topic_arn, 'SQS', self.queue_arn)








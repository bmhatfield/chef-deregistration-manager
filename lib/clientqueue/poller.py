import threading
import logging
import message


class QueuePoller(threading.Thread):
    def __init__(self, queue, handler, options, config):
        threading.Thread.__init__(self)
        self.queue = queue
        self.options = options
        self.messagehandler = handler

    def run(self):
        while len(self.queue) > 0:
            try:
                rawmessage = self.queue.dequeue()
                if rawmessage:
                    logging.info("Message found:\n%s", rawmessage)
                    msg = message.Message(rawmessage)

                    if not self.options.dry_run:
                        self.messagehandler.process(msg)
                else:
                    logging.warning("Disregarding empty message from queue. (SQS bug due to fast re-poll of queue.)")
                    continue
            except Exception as e:
                logging.exception("Exception while processing message:\n %s", str(e))
                continue

        logging.debug("Thread work complete.")

import json


class MessageFormat():
    """
    Defines interface and common methods for message formats.
    """
    required_params = []

    def __init__(self, raw_message):
        self.raw_message = raw_message

    @property
    def missing(self):
        return([x for x in self.required_params if x not in self.message])

    def get_message(self):
        if isinstance(self.raw_message, str) or isinstance(self.raw_message, unicode):
            return json.loads(self.raw_message)
        else:
            return self.raw_message

    def is_valid_format(self):
        message = self.get_message()

        if "type" in message:
            message_type = message['type']
        elif "Type" in message:
            message_type = message['Type']
        else:
            raise KeyError("Message missing 'Type' or 'type' key!")

        if message_type == self._type:
            return self.validate()
        else:
            return False

    def validate(self):
        if len(self.missing) > 0:
            raise ValueError("Matched Type '%s', but missing required parameters: %s" % (self.__class__.__name__, self.missing))
        else:
            return True


class RegistrationMessage(MessageFormat):
    """
    Class to handle messages of type "registration"
    """
    _type = 'registration'
    required_params = ["method", "nagios_name", "chef_name"]


class AutoscalingMessage(MessageFormat):
    """
    Class to handle messages from Amazon's Autoscaling -> SNS -> SQS workflow.
    """
    _type = 'Notification'
    required_params = ["Message", "TopicArn", "MessageId"]


class Message():
    """
    Generic Message class that automatically switches formats based upon message type.
    """
    supported = [RegistrationMessage, AutoscalingMessage]

    def __init__(self, raw_message):
        self.format = self.get_format(raw_message)
        self.message = self.format.message

    def get_format(self, raw_message):
        for format in self.supported:
            f = format(raw_message)

            if f.is_valid_format():
                return f

        raise ValueError("Message format unsupported.")

    def __repr__(self):
        return json.dumps(self.message)

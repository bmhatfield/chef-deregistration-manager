import json

class MessageFormat():
    """
    Defines interface and common methods for message formats.
    """
    required_params = None

    def __init__(self, raw_message):
        self.message = json.loads(raw_message)

        if "type" not in self.message:
            raise ValueError("Message missing 'type' key.")

    @property
    def missing(self):
        return([x for x in self.required_params if x not in self.message])

    def is_valid_format(self):
        if self.message['type'] == self._type:
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
    _type = ''
    required_params = [""]


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








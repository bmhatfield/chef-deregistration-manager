import json


class MessageFormat():
    """
    Defines interface and common methods for message formats.
    """
    required_params = []
    nested_message_key = False

    def __init__(self, raw_message):
        self.raw_message = raw_message

        self.message = self.get_message()

    @property
    def missing(self):
        if self.message:
            return([x for x in self.required_params if x not in self.message])
        else:
            return self.required_params

    def get_message(self):
        if isinstance(self.raw_message, str) or isinstance(self.raw_message, unicode):
            try:
                json_message = json.loads(self.raw_message)

                if self.nested_message_key:
                    if self.nested_message_key in json_message:
                        return json.loads(json_message[self.nested_message_key])
                    else:
                        raise KeyError("%s not in nested message of type %s" % (self.nested_message_key, self.__class__.__name__))
                else:
                    return json_message
            except ValueError:
                return self.raw_message

    def is_valid_format(self):
        if "type" in self.message:
            message_type = self.message['type']
        elif "Type" in self.message:
            message_type = self.message['Type']
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
    nested_message_key = "Message"
    required_params = ["EC2InstanceId", "Event", "AutoScalingGroupName"]


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

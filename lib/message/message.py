import json


class MessageFormat():
    """
    Defines interface and common methods for message formats.
    """
    required_params = []

    def __init__(self, raw_message):
        self.raw_message = raw_message

        try:
            self.json = json.loads(raw_message)
        except:
            self.json = False

        self.message = self.get_message()
        if not self.message:
            raise TypeError("Message not of type '%s'" % (self.__class__.__name__))

    def get_message(self):
        if self.json:
            return self.json
        else:
            return self.raw_message

    def validate(self, message):
        missing = [x for x in self.required_params if x not in message]
        if len(missing) > 0:
            raise ValueError("Matched Type '%s', but missing required parameters: %s" % (self.__class__.__name__, missing))
        else:
            return True


class RegistrationMessage(MessageFormat):
    """
    Class to handle messages of type "registration"
    """
    _type = 'registration'
    required_params = ["method", "nagios_name", "chef_name"]

    def get_message(self):
        if self.json:
            if 'type' in self.json and self.json['type'] == self._type:
                if self.validate(self.json):
                    return self.json

        return False


class AutoscalingMessage(MessageFormat):
    """
    Class to handle messages from Amazon's Autoscaling -> SNS -> SQS workflow.
    """
    _type = 'Notification'
    required_params = ["EC2InstanceId", "Event", "AutoScalingGroupName"]

    def get_message(self):
        if self.json:
            if "Type" in self.json and self.json["Type"] == self._type:
                if "Message" in self.json:
                    try:
                        message = json.loads(self.json["Message"])
                        if self.validate(message):
                            return message
                    except:
                        return False

        return False


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
            try:
                return format(raw_message)
            except TypeError:
                continue

        raise ValueError("Message format unsupported.")

    def __repr__(self):
        return json.dumps(self.message)

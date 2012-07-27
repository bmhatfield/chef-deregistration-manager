import json

class MessageFormat():
    """
    Generic JSON message class, defines general interface.
    """
    required_params = []

    def __init__(self, raw_message):
        self.message = json.loads(raw_message)

        if "type" not in self.message:
            raise ValueError("Message missing 'type' key.")

        self.validate()

    @property
    def missing(self):
        return([x for x in self.required_params if x not in self.message])

    def validate(self):
        if len(self.missing) > 0:
            raise ValueError("%s missing required parameters: %s" % (self.__class__.__name__, self.missing))


class RegistrationMessage(MessageFormat):
    """
    Class to handle messages of type "registration"
    """
    message_type = 'registration'
    required_params = ["nagios_name", "chef_name"]


class SNSMessage(MessageFormat):
    """
    Class to handle messages of type "registration"
    """

    message_type = ''
    required_params = [""]


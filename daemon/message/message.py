import json

class Message():
    """
    Generic JSON message class, defines general interface.
    """
    def __init__(self, raw_message):
        self.message = json.loads(raw_message)

        if "type" not in self.message:
            raise ValueError("Message missing 'type' key.")

        self.validate()

    def validate(self):
        raise NotImplementedError


class RegistrationMessage(Message):
    """
    Class to handle messages of type "registration"
    """

    required_params = ["nagios_name", "chef_name"]

    def validate(self):
        missing = [x for x in self.required_params if x not in self.message]
        if len(missing) > 0:
            raise ValueError("RegistrationMessage missing required parameters: %s" % (missing))
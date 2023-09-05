from office365.runtime.client_value import ClientValue


class EmailAddress(ClientValue):
    """The name and email address of a contact or message recipient."""

    def __init__(self, address=None, name=None):
        """
        :param str address:
        :param str name:
        """
        super(EmailAddress, self).__init__()
        self.address = address
        self.name = name

    def __repr__(self):
        return "{0} <{1}>".format(self.name, self.address)

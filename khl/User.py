class User:
    """ represents a user, used in TextMsg now
    """

    def __init__(self, data):
        # TODO: dara handler
        self.id = data['id']
        self.nickname = data['nickname']
        pass

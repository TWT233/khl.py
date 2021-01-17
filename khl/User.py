class User:
    """
    presents a User in chat/group

    including other bots
    """
    def __init__(self, data):
        self.id: str = data['id']
        self.nickname: str = data['nickname']
        pass

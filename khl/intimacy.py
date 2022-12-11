from typing import List, Tuple


class IntimacyInfo:
    img_url: str
    social_info: str
    last_read: int
    score: int
    img_list: List[Tuple[str, str]]

    def __init__(self, **kwargs) -> None:
        self.img_url = kwargs.get('img_url')
        self.social_info = kwargs.get('social_info')
        self.last_read = kwargs.get('last_read')
        self.score = kwargs.get('score')
        self.img_list = [(img.get('id'), img.get('url')) for img in kwargs.get('img_list')]

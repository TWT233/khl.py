from typing import List, overload


class Meta:
    id: str
    version: str
    name: str
    description: str
    author: [str, List[str]]
    link: str

    def __init__(self, module) -> None:
        try:
            meta = module.PLUGIN_METADATA
        except AttributeError:
            meta = {}
        self.id = meta.get('id', module.__name__.lower())
        self.name = meta.get('name', module.__name__)
        self.version = meta.get('version', '1.0.0')
        self.description = meta.get('description', '')
        self.author = meta.get('author', '')
        self.link = meta.get('link', '')


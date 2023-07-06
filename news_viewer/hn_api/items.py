

class HNBase:
    def __init__(self, id, type, **kwargs):
        self.id = id
        self.type = type

        self.deleted = kwargs.get("deleted", None)
        self.by = kwargs.get("by", None)
        self.time = kwargs.get("time", None)
        self.dead = kwargs.get("dead", None)
        self.kids = kwargs.get("kids", None)
        self.text = kwargs.get("text", None)


class HNStory(HNBase):
    def __init__(self, id, type, **kwargs):
        super().__init__(id, type, **kwargs)

        self.descendants = kwargs.get("descendants", None)
        self.score = kwargs.get("score", None)
        self.title = kwargs.get("title", None)
        self.url = kwargs.get("url", None)


class HNComment(HNBase):
    def __init__(self, id, type, **kwargs):
        super().__init__(id, type, **kwargs)
        self.parent = kwargs.get("parent", None)
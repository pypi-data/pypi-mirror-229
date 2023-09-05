class Parameter:
    def __init__(self,
                 type,
                 description):
        self.type = type
        self.description = description

    def __json__(self):
        return {
            "type": self.type,
            "description": self.description
        }

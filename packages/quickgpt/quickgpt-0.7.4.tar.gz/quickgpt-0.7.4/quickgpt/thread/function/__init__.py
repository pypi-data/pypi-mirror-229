class Function:
    def __init__(self,
                 name,
                 description,
                 properties,
                 required=[]):
        self.name = name
        self.description = description
        self.properties = properties
        self.required = required

    @property
    def __json__(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.properties,
                "required": self.required
            }
        }

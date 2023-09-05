import tiktoken

class Message(object):
    def __init__(self, content, sticky=False):
        self.content = content
        self.sticky = sticky

    @property
    def role(self):
        return self.__class__.__name__.lower()

    @property
    def obj(self):
        return {
            "role": self.role,
            "content": self.content
        }

    @property
    def message(self):
        return self.content

    def __str__(self):
        return "<%s> %s" % (self.role, self.content)

    def __len__(self):
        """ Returns the length of the content, in characters """
        return len(self.content)

    def get_tokens(self):
        """ Returns the length of the content, in tokens """
        tokenizer = tiktoken.get_encoding("cl100k_base")

        return len(tokenizer.encode(self.message))

class System(Message): pass
class User(Message): pass
class Assistant(Message):
    def __init__(self, content, function_call=None, sticky=False):
        self.content = content
        self.function_call = function_call
        self.sticky = sticky

    @property
    def obj(self):
        if self.function_call:
            return {
                "role": self.role,
                "function_call": self.function_call,
                "content": self.content
            }
        else:
            return {
                "role": self.role,
                "content": self.content
            }

class Function(Message):
    def __init__(self, name, content, sticky=False):
        self.name = name
        self.content = content
        self.sticky = sticky

    @property
    def obj(self):
        return {
            "role": self.role,
            "name": self.name,
            "content": str(self.content)
        }

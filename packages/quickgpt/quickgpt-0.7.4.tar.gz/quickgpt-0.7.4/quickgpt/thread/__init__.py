import openai
import time
import json
import tiktoken

from uuid import uuid4

from quickgpt.thread.messagetypes import *
from quickgpt.thread.response import Response

class Thread:
    def __init__(self, quickgpt, model):
        self.quickgpt = quickgpt
        self.model = model

        openai.api_key = quickgpt.api_key

        self.thread = []
        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

        self.id = str(uuid4())

        self.tokenizer = None

    def __len__(self):
        """ Returns the length of the Thread, by message count

        Returns:
            int: Length of thread by message count
        """

        return len(self.thread)

    def __getitem__(self, index):
        if type(index) not in (int, slice):
            raise TypeError("list indices must be integers or slices, not %s" % type(index))

        return self.thread[index]

    def __setitem__(self, index, value):
        self.thread[index] = value

    def get_tokens(self):
        """ Returns the tokens of the current thread, using OpenAI's tiktoken

        Currently hard-coded to use cl100k_base only for now.
        """

        if not self.tokenizer:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        tokens = []

        for message in self.thread:
            _token = self.tokenizer.encode(message.message)
            tokens += _token

        return tokens

    def get_tokens_length(self):
        """ Returns the length of the current thread, in tokens """

        return len(self.get_tokens())

    def serialize(self):
        """ Returns a serializable, JSON-friendly dict with all of the
        thread's data. Can be restored to a new Thread object later.

        Returns:
            dict: A JSON-safe representation of this thread, to be restored
                later using thread.restore()
        """

        return {
            "__quickgpt-thread__": {
                "id": self.id,
                "thread": self.messages,
                "usage": self.usage
            }
        }

    def restore(self, obj):
        """ Restores a serialized Thread object,
        provided by thread.serialize()

        Args:
            obj (dict): A dict returned from thread.serialize()

        Returns:
            None
        """

        thread_dict = obj["__quickgpt-thread__"]
        self.id = thread_dict["id"]

        if "usage" in obj:
            self.usage = obj["usage"]

        self.feed(thread_dict["thread"])

    def clear(self, include_sticky=False):
        """ Resets the thread, preserving only messages that were
        marked as sticky - unless include_sticky is set to True."""

        for message in self.thread:
            if not message.sticky or include_sticky:
                self.thread.remove(message)

    def feed(self, *messages, insert=None):
        """ Appends a new message to the end of the Thread feed. """

        try:
            # Check if the first argument is a list, and then make it the parent
            iter(messages[0])
            messages = messages[0]
        except TypeError:
            pass

        for msg in messages:
            assert type(msg) in (System, Assistant, User, Function, Response, dict), \
                "Must be of type System, Assistant, User, Function, Response, or dict"

            # Convert a boring old dict message to a pretty object message
            if type(msg) == dict:
                role = msg["role"]
                content = msg["content"]

                if role == "system":
                    msg = System(content)
                elif role == "assistant":
                    msg = Assistant(content)
                elif role == "user":
                    msg = User(content)
                elif role == "function":
                    name = msg["name"]
                    msg = Function(name, content)
                else:
                    raise TypeError("Unknown role '%s'" % role)

            if insert:
                self.thread.insert(insert, msg)
            else:
                self.thread.append(msg)

    def insert(self, index, *messages):
        """ Inserts messages at a given index in the Thread

        This method is currently not implemented.
        """

        self.feed(
            insert=True,
            *messages
        )

    @property
    def messages(self):
        """ Returns a JSON-safe list of all messages in this thread

        Returns:
            list: JSON-safe list of all messages
        """

        for msg in self.thread:
            if msg.obj["role"] == "assistant":
                if not msg.obj["content"] and "function_call" not in msg.obj:
                    self.thread.remove(msg)


        return [ msg.obj for msg in self.thread ]

    def run(self, *append_messages, feed=True, stream=False, functions=[]):
        """ Executes the current Thread and get a response. If ``feed`` is
        True, it will automatically save the response to the Thread.

        You can provide *append_messages that will only apply to this run(),
        and won't be permanently stored in the Thread.

        *functions allows you to define functions.

        Returns:
            Response: The resulting Response object from OpenAI
        """

        _functions = None

        if len(functions) > 0:
            _functions = []

            for function in functions:
                method = function["method"]
                description = function["description"]
                properties = function["properties"]
                required = function["required"]

                _function = {
                    "name": method.__name__,
                    "description": description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }

                _functions.append(_function)

        messages = self.messages
        append_messages = [ msg.obj for msg in append_messages ]

        for i in range(self.quickgpt.retry_count):
            try:
                if _functions:
                    response_obj = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages + append_messages,
                        stream=stream,
                        functions=_functions,
                        function_call="auto"
                    )
                else:
                    response_obj = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages + append_messages,
                        stream=stream
                    )

                break
            except openai.error.RateLimitError as e:
                if self.quickgpt.retry_count == i - 1:
                    print("Failed after %s tries" % self.quickgpt.retry_count)
                    raise e

                print("OpenAI returned RateLimitError, trying again after 10 sec...")

                time.sleep(10)
            except openai.error.InvalidRequestError as e:
                print(
                    json.dumps({
                        "messages": messages + append_messages,
                        "model": self.model
                    }, indent=2)
                )

                print("Please see failed request encoded as JSON above.")

                raise e

        response = Response(response_obj, stream=stream)

        # Get first segment, and test if function call. otherwise, pass on to client
        if response.message:
            for resp in response.message:

                if not response.has_function_call:
                    response.buffered = resp
                    break

        # If there's a function, override stream
        if response.has_function_call:
            name = response.function_call["name"]
            arguments = json.loads(response.function_call["arguments"])

            for f in functions:
                if f["method"].__name__ == name:
                    content = f["method"](**arguments)

            function = Function(name, content)

            if feed:
                self.feed(Assistant(None, function_call=response.function_call))
                self.feed(function)

            return function

        if feed:
            self.feed(response)

        return response

    def moderate(self, prompt):
        """ Validate a prompt to ensure it's safe for OpenAI's policies

        Args:
            prompt (str): The user's query to validate

        Returns:
            bool: True if it's flagged as a violation, False if it's safe
        """

        response = openai.Moderation.create(
            input=prompt
        )

        output = response["results"][0]["flagged"]

        return output

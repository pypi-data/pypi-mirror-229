from typing import Dict, List, Optional, TypedDict, Union

from martian import util


class Message(TypedDict):
    role: str
    content: str


class MartianRequestBody:
    messages: List[Message]
    model: str


class ChatCompletionChoice:
    index: int
    message: Message
    finish_reason: str


class CompletionChoice:
    text: str
    index: int
    logprobs: Optional[Dict]
    finish_reason: str


class MartianResponse:
    object: str
    choices: List[Union[CompletionChoice, ChatCompletionChoice]]


class MartianResource:
    __url = "https://route.withmartian.com/api/v1/generate"
    __headers = {"Content-Type": "application/json"}

    @classmethod
    def __get_other_params(cls, *args, **kwargs) -> Dict:
        res = dict()
        if args:
            res["args"] = args
        if kwargs:
            res["kwargs"] = kwargs
        return res

    @classmethod
    def create(cls, body: Dict, *args, **kwargs) -> Dict:
        body["other"] = cls.__get_other_params(*args, **kwargs)
        return util.send_request(cls.__url, body, cls.__headers)

    @classmethod
    async def acreate(cls, body: Dict, *args, **kwargs) -> Dict:
        body["other"] = cls.__get_other_params(*args, **kwargs)
        return await util.async_send_request(cls.__url, body, cls.__headers)


class ChatCompletion(MartianResource):
    @classmethod
    def __get_body(
        cls, messages: List[Message], model: Optional[str]
    ) -> MartianRequestBody:
        res = {
            "messages": messages,
        }
        if model is not None:
            res["model"] = f"openai/chat/{model}"
        return res

    @classmethod
    def __jsonify(cls, response: Dict) -> MartianResponse:
        if "error" in response:
            raise Exception(response["error"])

        choice = ChatCompletionChoice()
        choice.index = 0
        choice.message = response["output"][0]
        choice.finish_reason = "stop"
        res = MartianResponse()
        res.object = "chat.completion"
        res.choices = [choice]
        return res

    @classmethod
    def create(cls, messages: List[Message], model: str = None, *args, **kwargs):
        body: MartianRequestBody = cls.__get_body(messages, model)
        res = super().create(body, *args, **kwargs)
        return cls.__jsonify(res)

    @classmethod
    async def acreate(cls, messages: List[Message], model: str = None, *args, **kwargs):
        body: MartianRequestBody = cls.__get_body(messages, model)
        res = await super().acreate(body, *args, **kwargs)
        return cls.__jsonify(res)


class Completion(MartianResource):
    @classmethod
    def __get_body(cls, prompt: str, model: Optional[str]) -> MartianRequestBody:
        res = {
            "messages": [{"role": "user", "content": prompt}],
        }
        if model is not None:
            res["model"] = f"openai/completion/{model}"
        return res

    @classmethod
    def __jsonify(cls, response: Dict) -> MartianResponse:
        if "error" in response:
            raise Exception(response["error"])

        choice = CompletionChoice()
        choice.text = response["output"][0]["content"]
        choice.index = 0
        choice.logprobs = None
        choice.finish_reason = "length"
        response = MartianResponse()
        response.object = "text_completion"
        response.choices = [choice]
        return response

    @classmethod
    def create(cls, prompt: str, model: str = None, *args, **kwargs):
        body: MartianRequestBody = cls.__get_body(prompt, model)
        res = super().create(body, *args, **kwargs)
        return cls.__jsonify(res)

    @classmethod
    async def acreate(cls, prompt: str, model: str = None, *args, **kwargs):
        body: MartianRequestBody = cls.__get_body(prompt, model)
        res = await super().acreate(body, *args, **kwargs)
        return cls.__jsonify(res)

# Copyright (c) 2023 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, ClassVar, Dict, Optional, Tuple
from collections import defaultdict
import types

import erniebot
import erniebot.errors as errors
from erniebot.types import FilesType, HeadersType, ParamsType
from erniebot.response import EBResponse
from erniebot.resources.abc.creatable import Creatable
from erniebot.resources.resource import EBResource

from qianfan.resources.base import BaseResource
from qianfan.utils import log_info, _set_val_if_key_exists
from qianfan.resources.chat_completion import (
    ChatCompletion,
    QfChatCompletionAPIResource,
)

QIANFAN_DEFAULT_COMPLETION_MODEL = "ERNIE-Bot-turbo"
import time


class Completion(BaseResource):
    """
    QianFan Completion API Resource

    QianFan Completion is an agent for calling QianFan completion API.

    """

    def __init__(self, **kwargs: Any) -> None:
        """
        init Qianfan Completion

        Args:
            **kwargs (Any): ak, sk

        Returns:
            None

        """
        super().__init__(**kwargs)

    def _preprocess(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        preprocess before send request
        """
        # if user provide `model` and `model` is a chat model
        # use chat api to mock completions
        mock_using_chat_completion = (
            "model" in kwargs
            and kwargs["model"] in ChatCompletion()._supported_model_endpoint()
        )
        if mock_using_chat_completion:
            kwargs["endpoint"] = ChatCompletion()._get_endpoint_from_dict(**kwargs)
        else:
            # or it's a normal completion request
            kwargs["endpoint"] = self._get_endpoint_from_dict(**kwargs)
        kwargs["mock_using_chat_completion"] = mock_using_chat_completion
        return kwargs

    def do(self, **kwargs: Any):
        """
        创建Completion

        Args:
            **kwargs (dict): 包含参数的字典，包括'model'表示需要创建的模型名称

        Returns:
            None

        """
        kwargs = self._preprocess(**kwargs)
        return QfCompletionAPIResource.create(**kwargs)

    async def ado(self, **kwargs: Any):
        """
        aio 创建Completion

        Args:
            kwargs (Any): 包含参数的字典，包括'model'表示需要创建的模型名称

        Returns:
            None

        """
        kwargs = self._preprocess(**kwargs)
        return await QfCompletionAPIResource.acreate(**kwargs)

    def _supported_model_endpoint(self):
        """
        preset model list of Completions
        support model:
            None

        Args:
            None

        Returns:
            a dict which key is preset model and value is the endpoint

        """
        # no default model for completion
        # this is a trick
        return {"NONE": None}

    def _default_model(self):
        """
        default model of Completion: no model available

        Args:
            None

        Returns:
           "None"

        """
        # no default model for completion
        return "NONE"


class QfCompletionAPIResource(EBResource, Creatable):
    """
    QianFan Completion API Resource

    providing access to QianFan "completions" API.

    """

    # the prefix of the endpoint in "completions" qianfan url
    _URL_PREFIX = "completions"

    def _prepare_create(
        self, kwargs: Dict[str, Any]
    ) -> Tuple[
        str,
        Optional[ParamsType],
        Optional[HeadersType],
        Optional[FilesType],
        bool,
        Optional[float],
    ]:
        """
        Args:
            kwargs (Dict[str, Any]): `endpoint` and `input` are necessary

        Returns:
            Tuple[
                str,
                Optional[ParamsType],
                Optional[HeadersType],
                Optional[FilesType],
                bool,
                Optional[float]
            ]:

                * `url` (str): the url to be requested
                * `params` (Optional[ParamsType]): the params of the request
                * `headers` (Optional[HeadersType]): the header of the request
                * `files` (Optional[FilesType]): the files in the request
                * `stream` (bool): whether to enable stream response
                * `request_timeout` (Optional[float]): the timeout of the request

        Raises:
            QianfanError: will be thrown when kwargs include unexpected key or do not include the required key
        """
        REQUIRED_KEYS = {"endpoint", "prompt", "mock_using_chat_completion"}
        for key in REQUIRED_KEYS:
            if key not in kwargs or kwargs[key] is None:
                raise errors.ArgumentNotFoundError(f"Missing required key: {key}")

        prompt = kwargs["prompt"]

        params = {"prompt": prompt}
        if "user_id" in kwargs:
            params["user_id"] = kwargs["user_id"]

        headers = kwargs.get("headers", None)
        files = None
        stream = kwargs.get("stream", False)
        request_timeout = kwargs.get("request_timeout", None)

        url_prefix = self._URL_PREFIX
        if kwargs["mock_using_chat_completion"]:
            url_prefix = QfChatCompletionAPIResource._URL_PREFIX
            params["messages"] = [{"role": "user", "content": prompt}]
            del params["prompt"]
        url = f"/{url_prefix}/{kwargs['endpoint']}"
        log_info("requesting url: %s" % url)

        _set_val_if_key_exists(kwargs, params, "stream")
        _set_val_if_key_exists(kwargs, params, "temperature")
        _set_val_if_key_exists(kwargs, params, "top_p")
        _set_val_if_key_exists(kwargs, params, "penalty_score")
        _set_val_if_key_exists(kwargs, params, "user_id")
        _set_val_if_key_exists(kwargs, params, "functions")

        return url, params, headers, files, stream, request_timeout

    def _post_process_create(self, resp):
        """
        This is the function invoked after request the api.
        In order to mock completions with chat api, we need to change the `object`
        in response from "chat.completion" to "completion".

        `resp` could be EBResponse, Generator(stream) or AsyncGenerator(async stream)
        Since we need to keep the return value type and also change the generated value,
        use Wrapper to change the Generator.
        """

        class GeneratorWrapper:
            """
            wrapper for Generator
            """

            def __init__(self, source) -> None:
                """
                source is the original generator
                """
                self.source = source

            def __iter__(self):
                """
                get the value from original generator
                modify the "object" in value
                and yield
                """
                value = self.source.__next__()
                value.__setstate__({"object": "completion"})
                yield value

        class AsyncGeneratorWrapper:
            """
            wrapper for AsyncGenerator
            """

            def __init__(self, source):
                """
                source is the original async generator
                """
                self.source = source

            async def __aiter__(self):
                """
                get the value from original generator
                modify the "object" in value
                and yield
                """
                value = await self.source.__anext__()
                value.__setstate__({"object": "completion"})
                yield value

        # resp could be EBResponse, Generator(stream) or AsyncGenerator(async stream)
        # when it's EBResponse, means that it's not stream
        if isinstance(resp, EBResponse):
            resp.__setstate__({"object": "completion"})
            return resp
        # when it's async stream, resp would be AsyncGenerator
        # use wrapper to change the generated value
        elif isinstance(resp, types.AsyncGeneratorType):
            return AsyncGeneratorWrapper(resp)
        # when it's sync stream, resp would be Generator
        elif isinstance(resp, types.GeneratorType):
            return GeneratorWrapper(resp)

        return resp

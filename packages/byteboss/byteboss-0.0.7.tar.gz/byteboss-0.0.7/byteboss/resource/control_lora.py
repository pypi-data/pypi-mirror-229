from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio


class ControlLora(Engine):

    baseurl = None

    @classmethod
    def post(cls, payload):
        return super()._post(url=cls.baseurl + f'fal/queue/submit', body=payload)

    @classmethod
    async def apost(cls, payload):
        return await super()._apost(url=cls.baseurl + f'fal/queue/submit', body=payload)

    @classmethod
    def get(cls, request_id):
        return super()._get(url=cls.baseurl + f'fal/queue/{request_id}/get')

    @classmethod
    async def aget(cls, request_id):
        return await super()._aget(url=cls.baseurl + f'fal/queue/{request_id}/get')

    @classmethod
    def create(cls, image_url: str = "", prompt: str = DefaultPrompts.general_prompt, negative_prompt: str = "",
               seed: int = 0, control_lora: Literal["sketch", "canny", "depth", "recolor"] = "sketch",
               method: Literal['onepost', 'postget'] = 'postget'):

        payload = {
          "image_url": image_url,
          "prompt": prompt,
          "negative_prompt": negative_prompt,
          "seed": seed,
          "control_lora": control_lora
        }

        if method == 'onepost':
            return super()._post(url=cls.baseurl, body=payload)
        else:
            request_id = cls.post(payload)['request_id']
            while True:
                result = cls.get(request_id)

                if 'status' in result:
                    if result['status'] in [500, 422]:
                        return result
                    time.sleep(0.5)
                else:
                    return result

    @classmethod
    async def acreate(cls, image_url: str = "", prompt: str = DefaultPrompts.general_prompt, negative_prompt: str = "",
               seed: int = 0, control_lora: Literal["sketch", "canny", "depth", "recolor"] = "sketch",
               method: Literal['onepost', 'postget'] = 'postget'):

        payload = {
          "image_url": image_url,
          "prompt": prompt,
          "negative_prompt": negative_prompt,
          "seed": seed,
          "control_lora": control_lora
        }

        if method == 'onepost':
            return await super()._apost(url=cls.baseurl, body=payload)
        else:
            request_id = (await cls.apost(payload))['request_id']
            while True:
                result = await cls.aget(request_id)

                if 'status' in result:
                    if result['status'] in [500, 422]:
                        return result
                    await asyncio.sleep(0.5)
                else:
                    return result

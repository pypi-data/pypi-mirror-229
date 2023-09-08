from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio

class FCS(Engine):
    
    baseurl = None

    @classmethod
    def post(cls, payload):
        return super()._post(url=cls.baseurl+f'fal/queue/submit', body=payload)

    @classmethod
    async def apost(cls, payload):
        return await super()._apost(url=cls.baseurl+f'fal/queue/submit', body=payload)

    @classmethod
    def get(cls, request_id):
        return super()._get(url=cls.baseurl+f'fal/queue/{request_id}/get')

    @classmethod
    async def aget(cls, request_id):
        return await super()._aget(url=cls.baseurl+f'fal/queue/{request_id}/get')

    @classmethod
    def create(cls, prompt: str = DefaultPrompts.general_prompt, negative_prompt: str = "",
               style: str = 'cinematic-default', performance: Literal['Speed', 'Quality'] = "Speed",
               seed: str = random_seed(), aspect_ratio: str = "1024×1024", image_number: int = 1,
               method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "negative_prompt": negative_prompt,
          "style": style,
          "performance": performance,
          "seed": seed,
          "aspect_ratio": aspect_ratio,
          "image_number": image_number
        }

        if method == 'onepost':
            return super()._post(url=cls.baseurl, body=payload)
        else:
            request_id = cls.post(payload)['request_id']
            while True:
                result = cls.get(request_id)

                if 'status' in result:
                    if result['status'] == 500:
                        return result
                    time.sleep(0.5)
                else:
                    return result

    @classmethod
    async def acreate(cls, prompt: str = DefaultPrompts.general_prompt, negative_prompt: str = "",
                      style: str = 'cinematic-default', performance: Literal['Speed', 'Quality'] = "Speed",
                      seed: str = random_seed(), aspect_ratio: str = "1024×1024", image_number: int = 1,
                      method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "negative_prompt": negative_prompt,
          "style": style,
          "performance": performance,
          "seed": seed,
          "aspect_ratio": aspect_ratio,
          "image_number": image_number
        }

        if method == 'onepost':
            return await super()._apost(url=cls.baseurl, body=payload)
        else:
            request_id = (await cls.apost(payload))['request_id']
            while True:
                result = await cls.aget(request_id)

                if 'status' in result:
                    if result['status'] == 500:
                        return result
                    await asyncio.sleep(0.5)
                else:
                    return result

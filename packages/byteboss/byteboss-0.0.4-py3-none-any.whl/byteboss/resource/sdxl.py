from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio

class Sdxl(Engine):
    
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
    def create(cls, prompt: str = DefaultPrompts.general_prompt, seed: str = random_seed(),
               image_size: str = "square_hd", num_inference_steps: int = 30, guidance_scale: float = 7.5,
               negative_prompt: str = "", image_format: str = "png", method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "seed": seed,
          "image_size": image_size,
          "num_inference_steps": num_inference_steps,
          "guidance_scale": guidance_scale,
          "negative_prompt": negative_prompt,
          "image_format": image_format
        }

        if method == 'onepost':
            return super()._post(url=cls.baseurl, body=payload)
        else:
            request_id = cls.post(payload)['request_id']
            while True:
                result = cls.get(request_id)

                if 'status' in result:
                    time.sleep(0.5)
                else:
                    return result

    @classmethod
    async def acreate(cls, prompt: str = DefaultPrompts.general_prompt, seed: str = random_seed(),
                      image_size: str = "square_hd", num_inference_steps: int = 30, guidance_scale: float = 7.5,
                      negative_prompt: str = "", image_format: str = "png", method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "seed": seed,
          "image_size": image_size,
          "num_inference_steps": num_inference_steps,
          "guidance_scale": guidance_scale,
          "negative_prompt": negative_prompt,
          "image_format": image_format
        }

        if method == 'onepost':
            return await super()._apost(url=cls.baseurl, body=payload)
        else:
            request_id = (await cls.apost(payload))['request_id']
            while True:
                result = await cls.aget(request_id)

                if 'status' in result:
                    await asyncio.sleep(0.5)
                else:
                    return result


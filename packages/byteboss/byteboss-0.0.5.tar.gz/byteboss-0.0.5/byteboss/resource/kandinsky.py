from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio

class Kandinsky(Engine):

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
    def create(cls, prompt: str = DefaultPrompts.general_prompt, num_inference_steps: int = 100, width: int = 512,
               height: int = 512, guidance_scale: int = 4, negative_prompt: str = "", image_format: str = "jpeg",
               sampler: str = "p_sampler", prior_cf_scale: int = 4, prior_steps: int = 5,
               method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "num_inference_steps": num_inference_steps,
          "width": width,
          "height": height,
          "guidance_scale": guidance_scale,
          "negative_prompt": negative_prompt,
          "image_format": image_format,
          "sampler": sampler,
          "prior_cf_scale": prior_cf_scale,
          "prior_steps": prior_steps
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
    async def acreate(cls, prompt: str = DefaultPrompts.general_prompt, num_inference_steps: int = 100, width: int = 512,
                      height: int = 512, guidance_scale: int = 4, negative_prompt: str = "", image_format: str = "jpeg",
                      sampler: str = "p_sampler", prior_cf_scale: int = 4, prior_steps: int = 5,
                      method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
          "prompt": prompt,
          "num_inference_steps": num_inference_steps,
          "width": width,
          "height": height,
          "guidance_scale": guidance_scale,
          "negative_prompt": negative_prompt,
          "image_format": image_format,
          "sampler": sampler,
          "prior_cf_scale": prior_cf_scale,
          "prior_steps": prior_steps
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


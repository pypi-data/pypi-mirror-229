from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio


class MusicGen(Engine):

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
    def create(cls, model_version: str = 'melody', prompt: str = '', duration: int = 8, continuation: int = 0,
               normalization_strategy: str = "loudness", top_k: int = 250, top_p: int = 0, temperature: int = 1,
               classifier_free_guidance: int = 3, output_format: Literal['mp3', 'wav'] = 'mp3', seed: int = 0,
               method: Literal['onepost', 'postget'] = 'postget'):

        payload = {
          "model_version": model_version,
          "prompt": prompt,
          "duration": duration,
          "continuation": continuation,
          "normalization_strategy": normalization_strategy,
          "top_k": top_k,
          "top_p": top_p,
          "temperature": temperature,
          "classifier_free_guidance": classifier_free_guidance,
          "output_format": output_format,
          "seed": seed
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
    async def acreate(cls, model_version: str = 'melody', prompt: str = '', duration: int = 8, continuation: int = 0,
               normalization_strategy: str = "loudness", top_k: int = 250, top_p: int = 0, temperature: int = 1,
               classifier_free_guidance: int = 3, output_format: Literal['mp3', 'wav'] = 'mp3', seed: int = 0,
               method: Literal['onepost', 'postget'] = 'postget'):

        payload = {
          "model_version": model_version,
          "prompt": prompt,
          "duration": duration,
          "continuation": continuation,
          "normalization_strategy": normalization_strategy,
          "top_k": top_k,
          "top_p": top_p,
          "temperature": temperature,
          "classifier_free_guidance": classifier_free_guidance,
          "output_format": output_format,
          "seed": seed
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

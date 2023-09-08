from byteboss.const import *
from byteboss.resource.engines import Engine
from typing import Literal
import time
import asyncio

class SdLoras(Engine):

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
    def create(cls, model_name: str = "runwayml/stable-diffusion-v1-5", prompt: str = DefaultPrompts.lora_prompt,
               negative_prompt: str = DefaultPrompts.lora_negative_prompt, loras: list = [], seed: int = 0,
               image_size: str = "square_hd", num_inference_steps: int = 30, guidance_scale: float = 7.5,
               clip_skip: int = 0, model_architecture: str = 'sd', scheduler: str = "DPM++ 2M",
               image_format: str = "jpeg", num_images: int = 1, method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "loras": loras,
            "seed": seed,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "clip_skip": clip_skip,
            "model_architecture": model_architecture,
            "scheduler": scheduler,
            "image_format": image_format,
            "num_images": num_images
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
    async def acreate(cls, model_name: str = "runwayml/stable-diffusion-v1-5", prompt: str = DefaultPrompts.lora_prompt,
                      negative_prompt: str = DefaultPrompts.lora_negative_prompt, loras: list = [], seed: int = 0,
                      image_size: str = "square_hd", num_inference_steps: int = 30, guidance_scale: float = 7.5,
                      clip_skip: int = 0, model_architecture: str = 'sd', scheduler: str = "DPM++ 2M",
                      image_format: str = "jpeg", num_images: int = 1, method: Literal['onepost', 'postget'] = 'postget'):
        payload = {
            "model_name": model_name,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "loras": loras,
            "seed": seed,
            "image_size": image_size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "clip_skip": clip_skip,
            "model_architecture": model_architecture,
            "scheduler": scheduler,
            "image_format": image_format,
            "num_images": num_images
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


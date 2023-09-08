import random

class DefaultPrompts:
    lora_prompt = "Photo of a european medieval 40 year old queen, silver hair, highly detailed face, detailed eyes, \
    headshot, intricate crown, age spots, wrinkles"
    lora_negative_prompt = "cartoon, painting, illustration, (worst quality, low quality, normal quality:2)"

    general_prompt = "an astronaut in the jungle, cold color palette with butterflies in the background, highly detailed,\
     8k"

def random_seed():
    return random.randint(100000, 999999)


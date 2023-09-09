import random

class DefaultPrompts:
    lora_prompt = "Photo of a european medieval 40 year old queen, silver hair, highly detailed face, detailed eyes, \
    headshot, intricate crown, age spots, wrinkles"
    lora_negative_prompt = "cartoon, painting, illustration, (worst quality, low quality, normal quality:2)"

    general_prompt = "an astronaut in the jungle, cold color palette with butterflies in the background, highly detailed,\
     8k"


whisper_languages = ["en", "zh", "de", "es", "ru", "ko", "fr", "ja", "pt", "tr", "pl", "ca", "nl", "ar", "sv", "it",
                     "id", "hi", "fi", "vi", "he", "uk", "el", "ms", "cs", "ro", "da", "hu", "ta", "no", "th", "ur",
                     "hr", "bg", "lt", "la", "mi", "ml", "cy", "sk", "te", "fa", "lv", "bn", "sr", "az", "sl", "kn",
                     "et", "mk", "br", "eu", "is", "hy", "ne", "mn", "bs", "kk", "sq", "sw", "gl", "mr", "pa", "si",
                     "km", "sn", "yo", "so", "af", "oc", "ka", "be", "tg", "sd", "gu", "am", "yi", "lo", "uz", "fo",
                     "ht", "ps", "tk", "nn", "mt", "sa", "lb", "my", "bo", "tl", "mg", "as", "tt", "haw", "ln", "ha",
                     "ba", "jw", "su"]

def random_seed():
    return random.randint(100000, 999999)


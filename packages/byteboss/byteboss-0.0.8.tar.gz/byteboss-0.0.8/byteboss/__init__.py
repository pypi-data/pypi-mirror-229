import os
from byteboss.resource import (
    SdLoras,
    Sdxl,
    FCS,
    Kandinsky,
    MusicGen,
    Whisper,
    ControlLora
)
from .util import load, aload, success

api_key = os.environ.get('BB_API_KEY')
skip_auth = False

success("Welcome to byteboss client 0.0.8")

__all__ = [
    'SdLoras',
    'Sdxl',
    'FCS',
    'Kandinsky',
    'MusicGen',
    'Whisper',
    'Control_Lora',
    'api_key',
    'skip_auth',
    'load',
    'aload'
]


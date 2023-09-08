import os
from byteboss.resource import (
    SdLoras,
    Sdxl,
    FCS,
    Kandinsky,
    MusicGen
)
from .util import load, aload, success

api_key = os.environ.get('BB_API_KEY')
skip_auth = False

success("Welcome to byteboss client 0.0.5")

__all__ = [
    'SdLoras',
    'Sdxl',
    'FCS',
    'Kandinsky',
    'MusicGen',
    'api_key',
    'skip_auth',
    'load',
    'aload'
]


from colorama import Fore
from datetime import datetime
import requests
import aiohttp
from io import BytesIO

def error(msg):
    print(Fore.RED + f"ERROR / {datetime.now()}{Fore.RESET} : {msg}")

def log(msg):
    print(Fore.MAGENTA + f"LOG / {datetime.now()}{Fore.RESET} : {msg}")

def success(msg):
    print(Fore.GREEN + f"LOG / {datetime.now()}{Fore.RESET} : {msg}")

def warn(msg):
    print(Fore.YELLOW + f"WARNING / {datetime.now()}{Fore.RESET} : {msg}")

def failed(msg):
    print(Fore.RED + f"FAILED / {datetime.now()}{Fore.RESET} : {msg}")

def load(file_url):
    response = requests.get(file_url)
    return BytesIO(response.content)

async def aload(file_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            return BytesIO(await response.read())

def request(method, url, api_key=None, body=None, skip_auth=False):
    if skip_auth:
        headers = {'X-Fal-Target-Url': url, 'Content-Type': 'application/json'}
        url = 'https://serverless.fal.ai/api/_fal/proxy'
    else:
        headers = {'Authorization': f'Key {api_key}', 'Content-Type': 'application/json'}
    r = requests.request(method, url, json=body, headers=headers)
    if r.status_code != 200 and r.status_code != 202:
        error(f"Request returned error({r.status_code})\nDetails: {r.text}")
        return {'status': r.status_code, 'detail': r.text}
    return r.json()

async def arequest(method, url, api_key, body=None, skip_auth=False):
    if skip_auth:
        headers = {'X-Fal-Target-Url': url, 'Content-Type': 'application/json'}
        url = 'https://serverless.fal.ai/api/_fal/proxy'
    else:
        headers = {'Authorization': f'Key {api_key}', 'Content-Type': 'application/json'}
    async with aiohttp.ClientSession() as s:
        async with s.request(method, url, json=body, headers=headers) as r:
            if r.status != 200 and r.status != 202:
                error(f"Request returned error({r.status})\nDetails: {await r.text()}")
                return {'status': r.status, 'detail': await r.text()}
            return await r.json()
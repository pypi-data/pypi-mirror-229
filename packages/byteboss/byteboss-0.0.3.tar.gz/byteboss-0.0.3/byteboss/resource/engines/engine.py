from byteboss.util import *
import byteboss

class Engine:
    @classmethod
    def _post(cls, url, body):
        log(f' |POST| to {url} with payload:\n{body}')
        return request(method='post', url=url, api_key=byteboss.api_key, body=body, skip_auth=byteboss.skip_auth)

    @classmethod
    def _get(cls, url):
        log(f' |GET| to {url}')
        return request(method='get', url=url, api_key=byteboss.api_key, skip_auth=byteboss.skip_auth)

    @classmethod
    async def _apost(cls, url, body):
        log(f' |POST| to {url} with payload:\n{body}')
        return await arequest(method='post', url=url, api_key=byteboss.api_key, body=body, skip_auth=byteboss.skip_auth)

    @classmethod
    async def _aget(cls, url):
        log(f' |GET| to {url}')
        return await arequest(method='get', url=url, api_key=byteboss.api_key, skip_auth=byteboss.skip_auth)


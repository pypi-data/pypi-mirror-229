import requests
VERSION = "0.1.3"
def version():
    return VERSION

class Nameless:
    def __init__(self, url: str, apikey: str):
        self.url = url
        self.apikey = apikey
        self.headers = {
            "Authorization": "Bearer {}".format(self.apikey)
        }
    def info(self):
        r = requests.get("{}/info".format(self.url), headers=self.headers)
        return r.json()
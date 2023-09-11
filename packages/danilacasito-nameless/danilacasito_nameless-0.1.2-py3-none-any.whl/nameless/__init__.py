import requests
VERSION = "0.1.2"
def version():
    return VERSION

class Nameless:
    def __init__(self, url: str, apikey: str):
        self.url = url
        self.apikey = apikey
    def info(self):
        r = requests.get("{}/info".format(self.url))
        return r.json()
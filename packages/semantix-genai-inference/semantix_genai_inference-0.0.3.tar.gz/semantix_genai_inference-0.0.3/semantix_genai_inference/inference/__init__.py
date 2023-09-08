import os
from typing import Optional
from abc import ABC, abstractmethod

class SemantixGenClient(ABC):
    def __init__(self, inference_server_id: str, api_secret: Optional[str], 
                 version: Optional[str]="v0", server: Optional[str]="app.elemeno.ai"):
        self.inference_server_id = inference_server_id
        self.url = f"https://infserv-{inference_server_id}.{server}/{version}/inference"

        if not api_secret:
            api_secret = os.environ.get("SEMANTIX_API_SECRET")
        if not api_secret:
            raise Exception("No API secret provided. Either pass it as an argument or set the SEMANTIX_API_SECRET environment variable.")

        # set the Authorization header on aiohttp.ClientSession
        self.headers = {
            "Authorization": f"Bearer {api_secret}",
        }

    def add_header(self, key, value):
        self.headers[key] = value

    @abstractmethod
    def complete(self, **kwargs):
        pass

    

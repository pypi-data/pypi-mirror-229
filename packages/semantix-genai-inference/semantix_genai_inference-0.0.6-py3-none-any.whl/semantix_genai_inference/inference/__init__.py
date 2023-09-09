import os
from typing import Optional, List
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
    def generate(self, **kwargs):
        pass

class CohereClient(ABC):

    def __init__(self, api_key: Optional[str]=None, 
                 generate_model: Optional[str] = "command",
                 version: Optional[str] = "v1"):
        self._api_key = api_key
        self._generate_model = generate_model
        self._host = "https://api.cohere.ai"
        self._version = version

        if not api_key:
            api_key = os.environ.get("COHERE_API_KEY")
        if not api_key:
            raise Exception("No API key provided. Either pass it as an argument or set the COHERE_API_KEY environment variable.")

        # set the Authorization header on aiohttp.ClientSession
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }

    def add_header(self, key, value):
        self.headers[key] = value

    @abstractmethod
    def generate(self, prompt: str, num_generations: Optional[int],
                 stream: Optional[bool], max_tokens: Optional[int],
                 truncate: Optional[str], temperature: Optional[float],
                 preset: Optional[str], end_sequences: Optional[List[str]],
                 stop_sequences: Optional[List[str]], k: Optional[int], 
                 p: Optional[float], frequency_penalty: Optional[float],
                 presence_penalty: Optional[float], return_likelihoods: Optional[str],
                 logit_bias: Optional[dict]):
        """  Call cohere generate API to generates realistic text conditioned on a given input.

        Args:
            prompt (str): The input text that serves as the starting point for generating the response. Note: The prompt will be pre-processed and modified before reaching the model.
            num_generations (int, optional): The maximum number of generations that will be returned. Defaults to 1, min value of 1, max value of 5
            stream (bool, optional): When true, the response will be a JSON stream of events. Streaming is beneficial for user interfaces that render the contents of the response piece by piece, as it gets generated.
            max_tokens (int, optional): The maximum number of tokens the model will generate as part of the response. Note: Setting a low value may result in incomplete generations. Defaults to 20
            truncate (str, optional): One of NONE|START|END to specify how the API will handle inputs longer than the maximum token length.
            temperature (float, optional): A non-negative float that tunes the degree of randomness in generation. Lower temperatures mean less random generations. Defaults to 0.75, min value of 0.0, max value of 5.0.
            preset (str, optional): Identifier of a custom preset. A preset is a combination of parameters, such as prompt, temperature etc
            end_sequences (List[str], optional): The generated text will be cut at the beginning of the earliest occurence of an end sequence. The sequence will be excluded from the text
            start_sequences (List[str], optional): The generated text will be cut at the end of the earliest occurence of a stop sequence. The sequence will be included the text
            k (int, optional): Ensures only the top k most likely tokens are considered for generation at each step. Defaults to 0, min value of 0, max value of 500
            p (float, optional): Ensures that only the most likely tokens, with total probability mass of p, are considered for generation at each step. If both k and p are enabled, p acts after k. Defaults to 0. min value of 0.01, max value of 0.99
            frequency_penalty (float, optional): Used to reduce repetitiveness of generated tokens. The higher the value, the stronger a penalty is applied to previously present tokens, proportional to how many times they have already appeared in the prompt or prior generation
            presence_penalty (float, optional): Defaults to 0.0, min value of 0.0, max value of 1.0. Can be used to reduce repetitiveness of generated tokens. Similar to frequency_penalty, except that this penalty is applied equally to all tokens that have already appeared, regardless of their exact frequencies
            return_likelihoods (str, optional): One of GENERATION|ALL|NONE to specify how and if the token likelihoods are returned with the response. Defaults to NONE
            logit_bias (dict, optional): sed to prevent the model from generating unwanted tokens or to incentivize it to include desired tokens. The format is {token_id: bias} where bias is a float between -10 and 10
        """
        pass
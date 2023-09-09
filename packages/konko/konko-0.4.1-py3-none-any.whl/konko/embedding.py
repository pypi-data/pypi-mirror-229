from openai.api_resources.embedding import Embedding as _Embedding
from . import config

class Embedding(_Embedding):
    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new embedding for the provided input and parameters.

        See https://docs.konko.ai/reference/post_embeddings for a list
        of valid parameters.
        """
        headers = kwargs.get('headers') or {}
        if config.OPENAI_API_KEY:
            headers["X-OpenAI-Api-Key"] = config.OPENAI_API_KEY
        kwargs['headers'] = headers
        return super().create(*args, **kwargs)
    
    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new embedding for the provided input and parameters.

        See https://docs.konko.ai/reference/post_embeddings for a list
        of valid parameters.
        """
        headers = kwargs.get('headers') or {}
        if config.OPENAI_API_KEY:
            headers["X-OpenAI-Api-Key"] = config.OPENAI_API_KEY
        kwargs['headers'] = headers
        return super().acreate(*args, **kwargs)
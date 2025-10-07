from spdb.utils._keys import OPENAI_API_KEY
import os
from openai import OpenAI
from spdb.abs import get_abstract

def get_embedding(text: str,
                model: str = "text-embedding-3-small"
                ):
    """
    Get an embedding for a given text.
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model=model
    )
    embedding_vector = response.data[0].embedding
    return embedding_vector

def url_to_embedding(url: str):
    """
    Get an embedding for a given text.
    """
    abstract = get_abstract(url)
    return get_embedding(abstract)


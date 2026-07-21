from google import genai
import config

_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        if config.USE_VERTEXAI:
            _client = genai.Client(
                vertexai=True,
                project=config.PROJECT_ID,
            )
        else:
            _client = genai.Client(api_key=config.API_KEY)
    return _client

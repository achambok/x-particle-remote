from config.environments import config

# The Tavily package may not be installed (removed due to aiohttp dependency).
# Provide a dummy client to avoid import errors at runtime.
try:
    from tavily import TavilyClient
except ImportError:
    class TavilyClient:
        def __init__(self, api_key=None):
            # no-op
            self.api_key = api_key

        def search(self, query: str, max_results: int = 5):
            # return empty result so the tool remains functional without external API
            return {"results": []}

# instantiate client; if real package missing, dummy will be used

tavily = TavilyClient(api_key=config.TAVILY_API_KEY)

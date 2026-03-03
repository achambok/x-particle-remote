# formerly a Groq-based configuration, now switched to a generic
# OpenAI-compatible model (e.g. QWEN) using DashScope API key.
from langchain.chat_models import ChatOpenAI
from config.environments import config

# we expect DASHSCOPE_API_KEY to be set in environment (.env file)
# model_name may need to be adjusted to whatever QWEN variant you use.
model = ChatOpenAI(
    openai_api_key=config.DASHSCOPE_API_KEY,  # type: ignore
    temperature=config.TEMPERATURE,
    model_name="qwen"  # change if necessary (e.g. "qwen-7b" etc.)
)

# formerly a Groq-based configuration, now switched to a generic
# OpenAI-compatible model (e.g. QWEN via DashScope or OpenRouter)
from config.environments import config

# If an API key is provided we use a real LLM, otherwise fall back to a dummy model
if config.MISTRAL_API_KEY:
    # Use Mistral API for AI functionality
    import requests
    import json
    
    class MistralModel:
        def __init__(self):
            self.api_key = config.MISTRAL_API_KEY
            self.base_url = "https://api.mistral.ai/v1/chat/completions"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.tools = []
        
        def bind_tools(self, tools):
            """LangChain-compatible method to bind tools"""
            self.tools = tools
            return self
        
        def invoke(self, *args, **kwargs):
            # Handle both list of messages and dict with messages key
            if args:
                messages = args[0]
            else:
                messages = kwargs.get("messages", [])
            
            # Convert messages to the format expected by Mistral
            formatted_messages = []
            for msg in messages:
                if hasattr(msg, 'content'):
                    formatted_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, dict) and 'content' in msg:
                    formatted_messages.append({"role": "user", "content": msg['content']})
            
            payload = {
                "model": "mistral-large-latest",
                "messages": formatted_messages,
                "temperature": config.TEMPERATURE
            }
            
            try:
                response = requests.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract the content from the response
                content = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response from AI')
                
                # Return a mock object that has a content attribute
                class MistralResponse:
                    def __init__(self, content):
                        self.content = content
                        self.tool_calls = []  # Empty tool calls for now
                
                return MistralResponse(content)
                
            except Exception as e:
                print(f"Error calling Mistral API: {e}")
                # Return a mock response
                class MistralErrorResponse:
                    def __init__(self, content):
                        self.content = f"[Error: {e}]"
                        self.tool_calls = []
                return MistralErrorResponse(f"Error: {e}")

    model = MistralModel()
elif config.DASHSCOPE_API_KEY:
    # Use DashScope API for AI functionality
    import requests
    import json
    
    class QWENModel:
        def __init__(self):
            self.api_key = config.DASHSCOPE_API_KEY
            self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
            self.headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            self.tools = []
        
        def bind_tools(self, tools):
            """LangChain-compatible method to bind tools"""
            self.tools = tools
            return self
        
        def invoke(self, *args, **kwargs):
            # Handle both list of messages and dict with messages key
            if args:
                messages = args[0]
            else:
                messages = kwargs.get("messages", [])
            
            # Convert messages to the format expected by QWEN
            prompt = ""
            for msg in messages:
                if hasattr(msg, 'content'):
                    prompt += msg.content + "\n"
                elif isinstance(msg, dict) and 'content' in msg:
                    prompt += msg['content'] + "\n"
            
            payload = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                "parameters": {
                    "temperature": config.TEMPERATURE
                }
            }
            
            try:
                response = requests.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                result = response.json()
                
                # Extract the content from the response
                content = result.get('output', {}).get('text', 'No response from AI')
                
                # Return a mock object that has a content attribute
                class QWENResponse:
                    def __init__(self, content):
                        self.content = content
                        self.tool_calls = []  # Empty tool calls for now
                
                return QWENResponse(content)
                
            except Exception as e:
                print(f"Error calling QWEN API: {e}")
                # Return a mock response
                class QWENErrorResponse:
                    def __init__(self, content):
                        self.content = f"[Error: {e}]"
                        self.tool_calls = []
                return QWENErrorResponse(f"Error: {e}")

    model = QWENModel()
else:
    # Dummy model for offline testing: returns simple canned responses
    class DummyModel:
        def invoke(self, *args, **kwargs):
            # Handle both list of messages and dict with messages key
            if args:
                messages = args[0]
            else:
                messages = kwargs.get("messages", [])
            
            # mimic LangChain chat model output: just echo the last user message
            last = messages[-1].content if messages else ""
            return type("R", (), {"content": f"[dummy model] {last}", "tool_calls": []})()
        
        def bind_tools(self, tools):
            """LangChain-compatible method to bind tools"""
            return self

    model = DummyModel()

from langchain.chat_models import init_chat_model

from config.models.models import NeurologyReport

llm = init_chat_model("openai:gpt-4.1")

prompt = """
You are a neurologist and based on the previous anamnesis and physiological examination,
you have to derive 
"""


import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from .langchain_prompts import sql_prompt, heading_prompt, query_decomposition_prompt, fallback_heading_prompt
from chatbot_api.langchain.langchain_pg_memory import PostgresChatMessageHistory

api_key = os.getenv("OPEN_AI_API_KEY") or ""

llm = ChatOpenAI(model_name="gpt-4o", openai_api_key=api_key)

# memory = ConversationBufferWindowMemory(memory_key="history", k=5)
def get_memory(session_id, k=5):
    history = PostgresChatMessageHistory(session_id=session_id)
    return ConversationBufferWindowMemory(
        memory_key="history",
        chat_memory=history,
        return_messages=True,
        k=k
    )

sql_chain = LLMChain(llm=llm, prompt=sql_prompt)
heading_chain = LLMChain(llm=llm, prompt=heading_prompt)
fallback_heading_chain = LLMChain(llm=llm, prompt=fallback_heading_prompt)
query_decomposition_chain = LLMChain(llm=llm, prompt=query_decomposition_prompt)


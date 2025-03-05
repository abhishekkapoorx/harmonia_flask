import os
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

groq_api_key = "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"


# Initialize Groq Chat Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-8b-8192")

# Define System Instructions
system_message = SystemMessage(content="You are an AI health assistant for women, providing expert advice on health, diet, and well-being.")

# Request model
class ChatRequest(BaseModel):
    user_input: str

async def chat(input):
    messages = [system_message, HumanMessage(content=input)]
    response = llm.invoke(messages)
    return response


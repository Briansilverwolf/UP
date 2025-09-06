from langchain_community.chat_models import ChatZhipuAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os


model_gemini = "gemini-2.0-flash-exp"
gemini_key = "AI"
chat_model = ChatGoogleGenerativeAI(model = model_gemini,api_key = gemini_key)



model = "chatglm_pro"
api_key = "01"
Zhipullm = ChatZhipuAI(model=model, api_key=api_key)




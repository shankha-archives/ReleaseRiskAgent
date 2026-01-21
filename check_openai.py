import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv('backend/.env')

def check_openai():
    try:
        llm = ChatOpenAI(
            api_key=os.environ.get('OPENAI_API_KEY'),
            model="gpt-5.1",
            temperature=0.3
        )
        response = llm.invoke("Hello, are you working?")
        print(f"✅ OpenAI Connection works! Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Connection Failed: {e}")
        return False

if __name__ == "__main__":
    check_openai()

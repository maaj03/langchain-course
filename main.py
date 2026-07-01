from dotenv import load_dotenv

load_dotenv()
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI, tools
from langchain_tavily import TavilySearch

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
tools = [TavilySearch()]
agent = create_agent(model=llm, tools=tools)

def main():
    print("Hello, from langchain-course!")
    result = agent.invoke({"messages": [HumanMessage(content="Procure por 5 vagas de emprego para coordenador de serviços de TI, com foco em N1, Field Service, SAP e IA com n8n e Langchain, verifique no linkedin e na região de São Paulo, Brasil.")]})
    print(result)

if __name__ == "__main__":
    main()

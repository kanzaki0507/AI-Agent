from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain.output_parsers import JsonOutputToolsParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

@tool
def add(first_int: int, second_int: int) -> int:
    """Add two intergers."""
    return first_int+second_int

@tool
def exponentiate(base: int, exponent: int) -> int:
    """Exponentiate the base to the exponent power."""
    return base**exponent

@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers."""
    return first_int*second_int

llm_with_tools = llm.bind_tools([add, exponentiate, multiply])
chain = llm_with_tools | JsonOutputToolsParser()
chain.invoke("15 x 2192 を計算して")
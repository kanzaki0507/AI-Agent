from typing import Union
from operator import itemgetter
from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain.output_parsers import JsonOutputToolsParser
from langchain_core.runnables import Runnable, RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")

@tool
def add(first_int: int, second_int: int) -> int:
    """Add two integers."""
    return first_int + second_int

@tool
def exponentiate(base: int, exponent: int) -> int:
    """Exponentiate the base to the exponent power."""
    return base ** exponent

@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers"""
    return first_int * second_int

tools = [multiply, exponentiate, add]
tool_map = {tool.name: tool for tool in tools}

def call_tool(tool_invocation: dict) -> Union[str, Runnable]:
    tool = tool_map[tool_invocation["type"]]
    return RunnablePassthrough.assign(output=itemgetter("args") | tool)

llm_with_tools = llm.bind_tools([add, exponentiate, multiply])
chain = (
    llm_with_tools
    | JsonOutputToolsParser()
    # 並行で実行する　／　１つしかツールがない場合もlistで返ってくる
    | RunnableLambda(call_tool).map()
)
res = chain.invoke("""
以下の計算を行なって
- 100 たす 1000
- 1241 x 21314
- 4 ** 10
""")

print(res)
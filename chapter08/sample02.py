from langchain.agents import tool
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo")

@tool
def get_word_length(word: str) -> int:
    """Return the length of a word."""
    return len(word)

# tool_choice で指定すると必ず get_word_length を呼び出せる
llm_with_tools = llm.bind_tools([get_word_length], tool_choice='get_word_length')
res1 = llm_with_tools.invoke("なんか面白いこと言って")
print(res1)

# tool_choice 指定しないとつかってくれないことが多い（使ってくれることもある）
llm_with_tools = llm.bind_tools([get_word_length])
res2 = llm_with_tools.invoke("なんか面白いこと言って")
print(res2)
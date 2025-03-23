from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

class Item(BaseModel):
    item_name: str = Field(description="商品名")
    price: Optional[int] = Field(None, description="商品の値段")
    color: Optional[str] = Field(None, description="商品の色")

system = "与えられた商品の情報を構造化してください"
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{item_info}"),
    ]
)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
structured_llm = llm.with_structured_output(Item)
chain = prompt | structured_llm
res = chain.invoke({"item_info": "Tシャツ 赤 142,000円"})

print(res)
print(res.json(ensure_ascii=False))
print(chain.invoke({"item_info": "Tシャツ 142,000円"}))
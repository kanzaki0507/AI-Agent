# LangSmithとの連携

```pip install -U langchain langchain-openai```

```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="<your-api-key>"
LANGSMITH_PROJECT="pr-another-cenotaph-91"
OPENAI_API_KEY="<your-openai-api-key>"
```

```
from langchain_openai import ChatOpenAI

llm = ChatOpenAI()
llm.invoke("Hello, world!")
```
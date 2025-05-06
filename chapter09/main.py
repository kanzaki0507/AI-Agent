import streamlit as st
from langchain.agents import create_tool_calling_agent, AgentExecutor
from  langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_community.callbacks import StreamlitCallbackHandler

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

# custom tools
from tools.search_ddg import search_ddg
from tools.fetch_page import fetch_page


CUSTOM_SYSTEM_PROMPT = """

あなたは、ユーザーのリクエストに基づいてインターネットで調べ物を行うアシスタントです。
利用可能なツールを使用して、調査した情報を説明して下さい。
すでに知っていることだけに基づいて答えないでください。回答する前にできる限り検索を行って下さい。
（ユーザーが読むページを指定するなど、特別な場合は、検索する必要はありません。）

検索結果ページを見ただけでは情報があまりないと思われる場合は、次の2つのオプションを検討して試してみて下さい。

- 検索結果のリンクをクリックして、各ページのコンテンツにアクセスし、読んでみて下さい。
- 1ページが長すぎる場合は、3回以上ページ送りしないでください（メモリの負荷がかかるため）。
- 検索クエリを変更して、新しい検索を実行して下さい。
- 検索する内容に応じて検索に利用する言語を適切に変更して下さい。
 - 例えば、プログラミング関連の質問については英語で検索するのがいいでしょう。

 ユーザーは非常に忙しく、あなたほど自由ではありません。
 そのため、ユーザーの労力を節約するために、直接的な回答を提供して下さい。

 == 悪い回答の例 ==
 - これらのページを参照して下さい。
 - これらのページを参照してコードを書くことができます。
 - 次のページが役立つでしょう。

 == 良い解答の例 ==
 - これはサンプルコードです。 -- サンプルコードをここに --
 - あなたの質問の答えは -- 回答をここに --

解答の最後には、参照したページのURLを**必ず**記載して下さい。（これにより、ユーザーは回答を検証することがでます）

ユーザーが使用している言語で回答するようにして下さい。
ユーザーが日本語で質問した場合は、日本語で回答して下さい。ユーザーがスペイン語で質問した場合は、スペイン語で回答して下さい。
"""

def init_page():
    st.set_page_config(
        page_title="Web Browsing Agent",
        # page_icon="X"
    )
    st.header("Web Browsing Agent")
    st.sidebar.title("Options")

def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "こんにちは！なんでも質問をどうぞ！"}
        ]
        st.session_state['memory'] = ConversationBufferWindowMemory(
            return_messages=True,
            memory_key="chat_history",
            k=10
        )

def select_model():
    models = ("GPT-4", "Claude 3.5 Sonnet", "Gemini 1.5 Pro", "GPT-3.5(not recommended)")

    model = st.sidebar.radio("Choose a model:", models)

    if model == "GPT-3.5(not recommended)":
        return ChatOpenAI(
            temperature=0, model_name="gpt-3.5-turbo"
        )
    elif model == "GPT-4":
        return ChatOpenAI(
            temperature=0, model_name="gpt-4o"
        )
    elif model == "Claude 3.5 Sonnet":
        return ChatAnthropic(
            temperature=0, model_name="claude-3.5-sonnet-20240620"
        )
    elif model == "Gemini 1.5 Pro":
        return ChatGoogleGenerativeAI(
            temperature=0, model="gemini-1.5-pro-latest"
        )

def create_agent():
    tools = [search_ddg, fetch_page]
    prompt = ChatPromptTemplate.from_messages([
        ("system", CUSTOM_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    llm = select_model()
    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=st.session_state['memory']
    )

def main():
    init_page()
    init_messages()
    web_browsing_agent = create_agent()

    for msg in st.session_state['memory'].chat_memory.messages:
        st.chat_messages(msg.type).write(msg.content)
    
    if prompt := st.chat_input(placeholder="2023 FIFA 女子ワールドカップの優勝国は？"):
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant"):
            # コールバック関数の設定（エージェントの動作の可視化用）
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True
            )

            # エージェントを実行
            response = web_browsing_agent.invoke(
                {'input': prompt},
                config=RunnableConfig({'callbacks': [st_cb]})
            )
            st.write(response["output"])

if __name__ == '__main__':
    main()
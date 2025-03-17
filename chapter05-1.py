import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import tiktoken
from dotenv import load_dotenv

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import traceback

load_dotenv()
api_key = os.environ["OPENAI_API_KEY"]

SUMMARIZE_PROMPT = """以下のコンテンツについて、内容を300文字程度でわかりやすく要約して下さい。

========

{content}

========

日本語で書いてね！
"""

MODEL_PRICES = {
    "input": {
        "gpt-3.5-turbo": 0.5 / 1_000_000,
        "gpt-4o": 5 / 1_000_000,
        "claude-3-5-sonnet-20240620": 3 / 1_000_000,
        "gemini-1.5-pro-latest": 3.5 / 1_000_000
    },
    "output": {
        "gpt-3.5-turbo": 1.5 / 1_000_000,
        "gpt-4o": 15 / 1_000_000,
        "claude-3-5-sonnet-20240620": 15 / 1_000_000,
        "gemini-1.5-pro-latest": 10.5 / 1_000_000
    }
}

def init_page():
    st.set_page_config(
        page_title="Website Summarizer",
        page_icon="🤗"
    )
    st.header("Website Summarizer 🤗")
    st.sidebar.title("Options")

    # チャット履歴の初期化：message_historyがなければ作成
    if "message_history" not in st.session_state:
        st.session_state.message_history = [
            # System Promptを設定（'system'はSystem Promptを意味する）
            ("system", "You are a helpful assistant.")
        ]


def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    # clear_buttonが押された場合や、message_historyがまだ存在しない場合に初期化
    if clear_button or "message_history" not in st.session_state:
        st.session_state.message_history = [
            ("system", "You are a helpful assistant.")
        ]

def select_model():
    # スライダーを追加し、temperatureを0から2までの範囲で選択可能にする
    # 初期値は0.0、刻み幅は0.01とする
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)

    # 選択可能なモデルを増やす
    models = ("GPT-3.5", "GPT-4", "Claude 3.5 Sonnet", "Gemini 1.5 Pro")
    model = st.sidebar.radio("Choose a model:", models)
    if model == "GPT-3.5":
        # st.session_state.model_name = "gpt-3.5-turbo"
        return ChatOpenAI(
            api_key=api_key,
            temperature=temperature,
            # model_name=st.session_state.model_name
            model_name="gpt-3.5-turbo"
        )
    elif model == "GPT-4":
        # st.session_state.model_name = "gpt-4o"
        return ChatOpenAI(
            api_key=api_key,
            temperature=temperature,
            # model_name=st.session_state.model_name
            model_name="gpt-4o"
        )
    elif model == "Claude 3.5 Sonnet":
        # st.session_state.model_name = "claude-3-5-sonnet-20240620"
        return ChatAnthropic(
            temperature=temperature,
            # model_name=st.session_state.model_name
            model_name="claude-3-5-sonnet-20240620"
        )
    elif model == "Gemini 1.5 Pro":
        # st.session_state.model_name = "gemini-1.5-pro-latest"
        return ChatGoogleGenerativeAI(
            temperature=temperature,
            # model=st.session_state.model_name
            model="gemini-1.5-pro-latest"
        )

def init_chain():
    st.session_state.llm = select_model()
    prompt = ChatPromptTemplate.from_messages([
        *st.session_state.message_history,
        ("user", SUMMARIZE_PROMPT)
    ])
    output_parser = StrOutputParser()
    chain = prompt | st.session_state.llm | output_parser
    return chain

# def get_message_counts(text):
#     if "gemini" in st.session_state.model_name:
#         return st.session_state.llm.get_num_tokens(text)
#     else:
#         # Claude 3はtokenizerを公開していないのでtiktokenを使ってトークン数をカウント
#         if "gpt" in st.session_state.model_name:
#             encoding = tiktoken.encoding_for_model(st.session_state.model_name)
#         else:
#             # 仮のものを利用
#             encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
#         return len(encoding.encode(text))
    
# def calc_and_display_costs():
#     output_count = 0
#     input_count = 0
#     for role, message in st.session_state.message_history:
#         # tiktokenでトークン数をカウント
#         token_count = get_message_counts(message)
#         if role == "ai":
#             output_count += token_count
#         else:
#             input_count += token_count
    
#     # 初期状態でSystem Messageのみが履歴に入っている場合はまだAPIコールが行われていない
#     if len(st.session_state.message_history) == 1:
#         return
    
#     input_cost = MODEL_PRICES['input'][st.session_state.model_name] * input_count
#     output_cost = MODEL_PRICES['output'][st.session_state.model_name] * output_count
    
#     if "gemini" in st.session_state.model_name and (input_count + output_count) > 128000:
#         input_cost *= 2
#         output_cost *= 2
#     cost = output_cost + input_cost

#     st.sidebar.markdown("## Costs")
#     st.sidebar.markdown(f"**Total cost: ${cost:.5f}**")
#     st.sidebar.markdown(f"- Input cost: ${input_cost:.5f}")
#     st.sidebar.markdown(f"- Output cost: ${output_cost:.5f}")

def validate_url(url):
    """URLが有効かどうかを判定する関数"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_content(url):
    try:
        with st.spinner("Fetching Content ..."):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # なるべく本文の可能性が高い要素を取得する
            if soup.main:
                return soup.main.get_text()
            elif soup.article:
                return soup.article.get_text()
            else:
                return soup.body.get_text()
    except:
        st.write(traceback.format_exc())
        return None

def main():
    init_page()
    init_messages()
    chain = init_chain()

    for role, message in st.session_state.get("message_history", []):
        st.chat_message(role).markdown(message)
    
    # ユーザーの入力を監視
    if url := st.text_input("URL: ", key="input"):
        is_valid_url = validate_url(url)
        if not is_valid_url:
            st.write('Please input valid url')
        else:
            if content := get_content(url):
                st.markdown("## Summary")
                st.write_stream(chain.stream({"content": content}))
                st.markdown("---")
                st.markdown("## Original Text")
                st.write(content)
        

        # # 2. LLMの返答をStreaming表示する
        # with st.chat_message('ai'):
        #     response = st.write_stream(chain.stream({"content": SUMMARIZE_PROMPT}))

        # # 3. チャット履歴に追加
        # st.session_state.message_history.append(("user", SUMMARIZE_PROMPT))
        # st.session_state.message_history.append(("ai", response))

    # コストを計算して表示
    # calc_and_display_costs()

if __name__ == '__main__':
    main()
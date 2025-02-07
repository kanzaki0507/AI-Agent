import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    st.set_page_config(
        page_title="My Great ChatGPT",
        page_icon="🤗"
    )
    st.header("My Great ChatGPT 🤗")

    # チャット履歴の初期化：message_historyがなければ作成
    if "message_history" not in st.session_state:
        st.session_state.message_history = [
            # System Promptを設定（'system'はSystem Promptを意味する）
            ("system", "You are a helpful assistant.")
        ]
    
    # ChatGPTに質問を与えて回答を取り出す（パースする）処理を作成（1.-4.の処理）
    # 1. ChatGPTのモデルを呼び出すように設定
    # (デフォルトではGPT-3.5Turboが呼ばれる)
    llm = ChatOpenAI(temperature=0)

    # 2. ユーザの質問を受け取り、ChatGPTに渡すためのテンプレートを作成
    # テンプレートには過去のチャット履歴を含めるように設定
    prompt = ChatPromptTemplate.from_messages([
        *st.session_state.message_history,
        ("user", "{user_input}") # ここにあとでユーザの入力が入る
    ])

    # 3. ChatGPTの返答をパースするための処理を呼び出し
    output_parser = StrOutputParser()

    # 4. ユーザーの質問をChatGPTに渡し、返答を取り出す連続的な処理(chain)を作成
    # 各要素を｜（パイプ）でつなげて連続的な処理を作成するのがLCELの特徴
    chain = prompt | llm | output_parser

    # ユーザーの入力を監視
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        with st.spinner("ChatGPT is typing ..."):
            response = chain.invoke({"user_input": user_input})
        
        # ユーザーの質問を履歴に追加（'user'はユーザーの質問を意味する）
        st.session_state.message_history.append(("user", user_input))

        # ChatGPTの回答を履歴に追加（'assistant'はChatGPTの回答を意味する）
        st.session_state.message_history.append(("ai", response))
    
    # チャット履歴の表示
    for role, message in st.session_state.get("message_history",[]):
        st.chat_message(role).markdown(message)

if __name__ == '__main__':
    main()
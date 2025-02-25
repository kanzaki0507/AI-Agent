import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# model
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

def init_page():
    st.set_page_config(
        page_title="Ask My PDF(s)",
        page_icon="./img/icon02.png"
    )
    st.sidebar.title("Options")

def select_model(temperature=0):
    models = ("GPT-3.5", "GPT-4", "Claude 3.5 Sonnet", "Gemini 1.5 Pro")
    model = st.sidebar.radio("Choose a model:", models)
    if model == "GPT-3.5":
        return ChatOpenAI(
            temperature=temperature,
            model_name="gpt-3.5-turbo"
        )
    elif model == "GPT-4":
        return ChatOpenAI(
            temperature=temperature,
            model_name="gpt-4o"
        )
    elif model == "Claude 3.5 Sonnet":
        return ChatAnthropic(
            temperature=temperature,
            model_name="claude-3-5-sonnet-20240620"
        )
    elif model == "Gemini 1.5 Pro":
        return ChatGoogleGenerativeAI(
            temperature=temperature,
            model="gemini-1.5-pro-latest"
        )

def init_qa_chain():
    llm = select_model()
    prompt = ChatPromptTemplate.from_template("""
    以下の前提知識を用いて、ユーザーからの質問に答えてください。
    
    ===
    前提知識
    {context}
    
    ===
    ユーザーからの質問
    {question}
    """)
    retriever = st.session_state.vectorstore.as_retriever(
        # "mmr", "similarity_score_threshold" などもある
        search_type="similarity",
        # 文書を何個取得するか (default: 4)
        search_kwargs={"k": 10}
    )
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

def page_ask_my_pdf():
    chain = init_qa_chain()

    if query := st.text_input("PDFへの質問を書いてください：", key="input"):
        st.markdown("### Answer")
        st.write_stream(chain.stream(query))

def main():
    init_page()
    st.title("PDf QA")
    if "vectorstore" not in st.session_state:
        st.warning("まずは Upload PDF(s) からPDFファイルをアップロードしてください")
    else:
        page_ask_my_pdf()

if __name__ == '__main__':
    main()
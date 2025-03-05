import streamlit as st

def init_page():
    st.set_page_config(
        page_title="Ask My PDF(s)",
    )

def main():
    init_page()

    st.sidebar.success("👆のメニューから進んでください。")
    st.markdown("""
    ### Ask My PDF(s)にようこそ！
    - このアプリでは、アップロードしたPDFに対して質問をすることができます。
    - まずは左のメニューから `Upload PDF(s)` を選択してPDFをアップロードして下さい。
    - PDFをアップロードしたら `PDF QA` を選択して質問をしてみましょう！

    """
    )

if __name__ == '__main__':
    main()
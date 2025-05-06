from itertools import islice
from duckduckgo_search import DDGS
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import (BaseModel, Field)

"""
Sample Response of DuckDuckGo python library
--------------------------------------------
[
    {
        'title': '日程・結果' | FIFA 女子ワールドカップ オーストラリア&ニュージーランド 2023 | なでしこジャパン | 日本代表 | Jfa | 日本サッカー協会',
        'href': 'XXX'
        'body': '日程・結果' | Fifa 女子ワールドカップ オーストラリア&ニュージーランド 2023.'
    },...
]
"""


class SearchDDGInput(BaseModel):
    query: str = Field(description="検索したいキーワードを入力して下さい")

@tool(args_schema=SearchDDGInput)
def search_ddg(query, max_result_num=5):
    """
    DuckDuckGo検索を実行するためのツールです。
    検索したいキーワードを入力して使用して下さい。
    検索結果の各ページのタイトル、スニペット（説明文）、URLが返されます。
    このツールから得られる説明文は非常に簡潔で、時には古い情報の場合もあります。

    必要な情報が見つからない場合は、必ず `fetch_page` ツールを使用して各ページの内容を確認して下さい。
    文脈に応じて最も適切な言語を使用して下さい（ユーザーの言語と同じである必要はありません）。
    例えば、プログラミング関連の質問では、英語で検索するのが最適です。

    Returns
    -------
    List[Dict[str, str]]:
    - title
    - snippet
    - url
    """

    res  =DDGS().text(query, region='wt-wt', safesearch='off', backend="lite")

    return [
        {
            "title": r.get('title', ""),
            "snippet": r.get('body', ""),
            "url": r.get('href', "")
        }
        for r in islice(res, max_result_num)
    ]
from shiny import reactive, render, ui

def search_logic(input, output, session):
    search_result = reactive.Value(None)

    # 検索ボタン押下でデータ取得
    @reactive.Effect
    def perform_search():
        input.compare_search_btn()
        code = input.select()
        company = input.fruits()
        if code and company:
            # ここでAPIやデータ取得
            search_result.set(f"{company}({code}) のデータ")

    # サイドバーのボタンでタブ切替
    @reactive.Calc
    def selected_tab():
        if input.btn1():
            return "企業概要"
        if input.btn2():
            return "財務情報"
        if input.btn3():
            return "株価情報"
        return "企業概要"

    # main_tab_content に出力
    @output
    @render.ui
    def main_tab_content():
        tab = selected_tab()
        data = search_result.get()
        if tab == "企業概要":
            return ui.p(f"企業概要: {data}")
        elif tab == "財務情報":
            return ui.p(f"財務情報: {data}")
        elif tab == "株価情報":
            return ui.p(f"株価情報: {data}")
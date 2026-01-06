from shiny import reactive, render, ui
import pandas as pd
from server.tabs import company_overview, financials, stock_indicators
from server.data_company_to_code import CODE_TO_COMPANY, COMPANY_TO_CODE

def search_logic(input, output, session):
    active_tab = reactive.value("home")
    selected_code = reactive.value('') # 選択された証券コードを管理

    # 選択ボックスの動的生成
    @render.ui
    def select_code_ui():
        # 証券コードをソートして表示
        sorted_codes = sorted(CODE_TO_COMPANY.keys())
        return ui.input_selectize(
            "select_code", 
            "証券コード", 
            choices=sorted_codes,
            selected=selected_code(),
            options={"placeholder": "証券コードを選択してください"}
        )
    
    @render.ui
    def select_company_ui():
        code = selected_code()
        company = CODE_TO_COMPANY.get(code, "")
        # 企業名をソートして表示
        sorted_companies = sorted(CODE_TO_COMPANY.values())
        return ui.input_selectize(
            "select_company",
            "企業名",
            choices=sorted_companies,
            selected=company,
            options={"placeholder": "企業名を選択してください"}
        )
    
    # データ統計情報を表示（デバッグ用）
    @render.text
    def data_info():
        return f"読み込まれた企業数: {len(CODE_TO_COMPANY)}"
    
    # 証券コードが変更されたときの処理
    @reactive.effect
    @reactive.event(input.select_code)
    def _():
        if input.select_code():
            selected_code.set(input.select_code())
    
    # 企業名が変更されたときの処理
    @reactive.effect
    @reactive.event(input.select_company)
    def _():
        if input.select_company():
            code = COMPANY_TO_CODE.get(input.select_company())
            if code and code != selected_code():
                selected_code.set(code)

    @reactive.effect
    @reactive.event(input.btn1)
    def _():
        active_tab.set("企業概要")
       
    @reactive.effect
    @reactive.event(input.btn2)
    def _():
        active_tab.set("財務情報")
    
    @reactive.effect
    @reactive.event(input.btn3)
    def _():
        active_tab.set("株価・投資指標")

    @render.ui
    def main_tab_content():
        current_tab = active_tab()
        if current_tab == "企業概要":
            return company_overview.ui_content(input, output, session)
        elif current_tab == "財務情報":
            return financials.ui_content(input, output, session)
        elif current_tab == "株価・投資指標":
            return stock_indicators.ui_content(input, output, session)
        else:
            return company_overview.ui_content(input, output, session)
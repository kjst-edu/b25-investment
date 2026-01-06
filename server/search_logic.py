from shiny import reactive, render, ui
import pandas as pd
from server.tabs import company_overview, financials, stock_indicators
from server.data_company_to_code import CODE_TO_COMPANY, COMPANY_TO_CODE, CODE_TO_INDUSTRY, INDUSTRY_TO_CODES

def search_logic(input, output, session):
    active_tab = reactive.value("home")
    selected_code = reactive.value('')  # 選択された証券コードを管理
    selected_industry = reactive.value('全業界')  # 選択された業界を管理

    # 業界選択ボックス
    @render.ui
    def select_industry_ui():
        industries = ['全業界'] + sorted(INDUSTRY_TO_CODES.keys())
        return ui.input_selectize(
            "select_industry",
            "業界で絞り込み",
            choices=industries,
            selected=selected_industry(),
            options={"placeholder": "業界を選択"}
        )

    # 証券コード選択ボックス（業界によるフィルタリング付き）
    @render.ui
    def select_code_ui():
        industry = selected_industry()
        
        if industry == '全業界':
            # 全ての証券コードを表示
            available_codes = sorted(CODE_TO_COMPANY.keys())
        else:
            # 選択された業界の証券コードのみ表示
            available_codes = sorted(INDUSTRY_TO_CODES.get(industry, []))
        
        # 現在選択されているコードが利用可能なコードに含まれているかチェック
        current_selected = selected_code()
        if current_selected and current_selected not in available_codes:
            current_selected = ""
        
        return ui.input_selectize(
            "select_code",
            "証券コード",
            choices=available_codes,
            selected=current_selected,
            options={"placeholder": "証券コードを選択してください"}
        )
    
    # 企業名選択ボックス（業界によるフィルタリング付き）
    @render.ui
    def select_company_ui():
        code = selected_code()
        company = CODE_TO_COMPANY.get(code, "")
        
        industry = selected_industry()
        
        if industry == '全業界':
            # 全ての企業名を表示
            available_companies = sorted(CODE_TO_COMPANY.values())
        else:
            # 選択された業界の企業名のみ表示
            available_codes = INDUSTRY_TO_CODES.get(industry, [])
            available_companies = sorted([CODE_TO_COMPANY[code] for code in available_codes])
        
        return ui.input_selectize(
            "select_company",
            "企業名",
            choices=available_companies,
            selected=company,
            options={"placeholder": "企業名を選択してください"}
        )
    
    # データ統計情報を表示
    @render.text
    def data_info():
        industry = selected_industry()
        if industry == '全業界':
            count = len(CODE_TO_COMPANY)
            return f"読み込まれた企業数: {count}"
        else:
            count = len(INDUSTRY_TO_CODES.get(industry, []))
            return f"「{industry}」の企業数: {count}"
        
    # 業界が変更されたときの処理
    @reactive.effect
    @reactive.event(input.select_industry)
    def _():
        if input.select_industry():
            selected_industry.set(input.select_industry())
            # 業界が変わったら証券コードの選択をリセット
            selected_code.set("")
    
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
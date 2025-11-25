from shiny import reactive, render, ui
from server.tabs import company_overview, financials, stock_indicators

CODE_TO_COMPANY = {
    "7203.T": "トヨタ自動車",
    "7974.T": "任天堂",
    "9984.T": "ソフトバンクG"
}
COMPANY_TO_CODE = {v: k for k, v in CODE_TO_COMPANY.items()}  # 逆引き辞書

def search_logic(input, output, session):
    active_tab = reactive.value("home")
    
    """
    # 最後に更新されたのがどちらかを記録
    last_updated = reactive.value("none")
    
    @reactive.effect
    def sync_selections():
        code = input.select_code()
        company = input.select_company()
        
        if last_updated.get() == "code" and code:
            # 証券コードが更新された場合
            expected_company = CODE_TO_COMPANY.get(code)
            if expected_company and expected_company != company:
                ui.update_selectize("select_company", selected=expected_company)
                last_updated.set("none")
        
        elif last_updated.get() == "company" and company:
            # 企業名が更新された場合
            expected_code = None
            for k, v in CODE_TO_COMPANY.items():
                if v == company:
                    expected_code = k
                    break
            if expected_code and expected_code != code:
                ui.update_selectize("select_code", selected=expected_code)
                last_updated.set("none")
    
    @reactive.effect
    @reactive.event(input.select_code)
    def _():
        last_updated.set("code")
    
    @reactive.effect
    @reactive.event(input.select_company)
    def _():
        last_updated.set("company")
    """

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
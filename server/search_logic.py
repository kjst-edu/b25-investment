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
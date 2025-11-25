from shiny import reactive, render, ui
import yfinance as yf
from server.explanations import EXPLANATIONS

CODE_TO_COMPANY = {
    "7203.T": "トヨタ自動車",
    "7974.T": "任天堂",
    "9984.T": "ソフトバンクG"
}

def ui_content(input, output, session):
    @output
    @render.ui
    @reactive.event(input.select_code)
    def select_company_ui():
        code = input.select_code()
        company = CODE_TO_COMPANY.get(code, "")
        return ui.input_selectize(
            "select_company",
            "企業名",
            list(CODE_TO_COMPANY.values()),
            selected=company
        )
    
    @render.text
    def company_name():
        if input.select_company():
            return input.select_company()
        else:
            return "企業を選択してください"

    @reactive.calc
    def ticker():
        return yf.Ticker(input.select_code())
    
    @render.ui
    def price():
        info = ticker().info
        price = info.get("currentPrice")
        prev = info.get("previousClose")

        if not price or not prev:
            return "―"

        change = price - prev
        change_percent = (change / prev) * 100
        sign = "+" if change >= 0 else "−"
        color = "red" if change >= 0 else "blue"

        return ui.HTML(
            f'<span style="font-size:30px;">{price:,.0f}'
            f'<span style="font-size:13px;"> 円</span></span> '
            f'<span style="font-size:13px;"> 前日比</span></span> '
            f'<span style="color:{color}; font-size:13px; margin-left:4px;">'
            f'({sign}{abs(change):,.0f} 円 / {sign}{abs(change_percent):.2f}%)'
            f'</span>'
        )
    
    @render.ui
    def market_cap():
        info = ticker().info
        mc = info.get("marketCap")
        
        if not mc:
            return "―"

        # 億円に変換
        mc_oku = mc / 100_000_000

        # HTML で文字サイズと右寄せを指定
        return ui.HTML(
            f'<div style="font-size:28px;">{mc_oku:,.1f}'
            f'<span style="font-size:13px;"> </span></div>'
            f'<div style="text-align:right; font-size:13px;">億円</div>'
        )
    
    @render.ui
    def per():
        info = ticker().info
        per = info.get("trailingPE")
        return f"{per:.2f}" if per else "―"
    
    @render.ui
    def roe():
        info = ticker().info
        roe = info.get("returnOnEquity")
        return f"{roe*100:.1f}%" if roe else "―"
    
    @render.ui
    def equity_ratio():
        info = ticker().info
        debt_to_equity = info.get("debtToEquity")
        if debt_to_equity:
            ratio = 100 / (1 + debt_to_equity)
            return f"{ratio:.1f}%"
        else:
            return "―"
    
    @render.ui
    def dividend_yield():
        info = ticker().info
        dividend = info.get("dividendYield")
        return f"{dividend:.2f}%" if dividend else "―"
    
    company_info_2 = ui.TagList(
        # ここがメイン表示部分
        ui.div(
            ui.h2(ui.output_text("company_name"), style="text-align: center; margin-bottom: 20px; color: #333;"),
            style="margin-bottom: 15px;"
        ),
            ui.layout_columns(
            ui.value_box(
                "現在の株価",
                ui.output_ui("price"),
            ),
            ui.value_box(
                "時価総額",
                ui.output_ui("market_cap"),
            ),
            ui.value_box(
                ui.tooltip(
                    ui.span(
                        "PER ",
                        ui.tags.span(
                            "?", 
                            style="""
                                color: white; 
                                background-color: #007bff; 
                                border-radius: 50%; 
                                width: 16px; 
                                height: 16px; 
                                display: inline-flex; 
                                align-items: center; 
                                justify-content: center; 
                                font-size: 11px; 
                                font-weight: bold; 
                                cursor: help; 
                                margin-left: 4px;
                            """
                        )
                    ),
                    EXPLANATIONS["per"]
                ),
                ui.output_ui("per"),
            ),
            ui.value_box(
                ui.tooltip(
                    ui.span(
                        "ROE ",
                        ui.tags.span(
                            "?", 
                            style="""
                                color: white; 
                                background-color: #007bff; 
                                border-radius: 50%; 
                                width: 16px; 
                                height: 16px; 
                                display: inline-flex; 
                                align-items: center; 
                                justify-content: center; 
                                font-size: 11px; 
                                font-weight: bold; 
                                cursor: help; 
                                margin-left: 4px;
                            """
                        )
                    ),
                    EXPLANATIONS["roe"]
                ),
                ui.output_ui("roe"),
            ),
            ui.value_box(
                "自己資本比率",
                ui.output_ui("equity_raito"),
            ),
            ui.value_box(
                "配当利回り",
                ui.output_ui("dividend_yield"),
            ),
            fill=False,
            ),
        )
    return company_info_2
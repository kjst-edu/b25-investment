from shiny import reactive, render, ui
from explanations import EXPLANATIONS

CODE_TO_COMPANY = {
    "1A": "トヨタ",
    "1B": "任天堂",
    "1C": "ソフトバンク"
}

def search_logic(input, output, session):

    company_info = ui.TagList(
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
                "ROE",
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


    active_tab = reactive.value("home")

    # 証券コードに応じて企業名を同期
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
            return company_info
        if current_tab == "財務情報":
            return ui.HTML("<h3>財務情報をここに表示</h3>")
        if current_tab == "株価・投資指標":
            return ui.HTML("<h3>株価・投資指標をここに表示</h3>")
        else:
            return company_info




"""
    # 「企業概要」ボタン押下時
    @reactive.Effect
    @reactive.event(input.btn1)
    def show_company_summary():
        output.main_tab_content.set(
            ui.layout_column_wrap(
                ui.value_box("Current Price", ui.output_ui("price")),
                ui.value_box("Change", ui.output_ui("change")),
                ui.value_box("Percent Change", ui.output_ui("change_percent")),
                fill=False,
            )
        )

    # 「財務情報」ボタン
    @reactive.Effect
    @reactive.event(input.btn2)
    def show_financial_info():
        output.main_tab_content.set(ui.HTML("<h3>財務情報をここに表示</h3>"))

    # 「株価情報」ボタン
    @reactive.Effect
    @reactive.event(input.btn3)
    def show_stock_info():
        output.main_tab_content.set(ui.HTML("<h3>株価情報をここに表示</h3>"))
"""
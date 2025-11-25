from shiny import reactive, render, ui

CODE_TO_COMPANY = {
    "1A": "トヨタ",
    "1B": "任天堂",
    "1C": "Grape"
}

def search_logic(input, output, session):

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

from shiny import ui, render, reactive

CODE_TO_COMPANY = {
    "1A": "トヨタ",
    "1B": "任天堂",
    "1C": "Grape"
}

search_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_selectize("select_code", "証券コード", list(CODE_TO_COMPANY.keys())),
            ui.input_selectize("select_company", "企業名", list(CODE_TO_COMPANY.values())),
            ui.input_action_button("search_btn", "検索"),
            ui.hr(),
            ui.input_action_button("btn1", "企業概要"),
            ui.input_action_button("btn2", "財務情報"),
            ui.input_action_button("btn3", "株価・投資指標"),
        ),
        ui.output_ui("main_tab_content"),
    )
)
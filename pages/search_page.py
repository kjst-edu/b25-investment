from shiny import ui, render, reactive

CODE_TO_COMPANY = {
    "7203.T": "トヨタ自動車",
    "7974.T": "任天堂",
    "9984.T": "ソフトバンクG"
}

search_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.output_ui("select_code_ui"),
            ui.output_ui("select_company_ui"),
            ui.input_action_button("search_btn", "検索"),
            ui.hr(),
            ui.input_action_button("btn1", "企業概要"),
            ui.input_action_button("btn2", "財務情報"),
            ui.input_action_button("btn3", "株価・投資指標"),
        ),
        ui.output_ui("main_tab_content"),
    )
)
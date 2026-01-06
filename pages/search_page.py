from shiny import ui, render, reactive
from server.data_company_to_code import CODE_TO_COMPANY, COMPANY_TO_CODE

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

# search_page.pyのどこかに追加
ui.div(
    ui.output_text("data_info"),
    style="font-size: 12px; color: #6c757d; margin-bottom: 10px;"
)
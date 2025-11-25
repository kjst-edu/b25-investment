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
            ui.input_action_button("btn3", "株価情報"),
        ),
        ui.output_ui("main_tab_content"),

        # ここがメイン表示部分
        ui.layout_column_wrap(
        ui.value_box(
            "Current Price",
            ui.output_ui("price"),
        ),
        ui.value_box(
            "Change",
            ui.output_ui("change"),
        ),
        ui.value_box(
            "Percent Change",
            ui.output_ui("change_percent"),
        ),
        fill=False,
        ),
    )
)
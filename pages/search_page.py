from shiny import ui, render, reactive

search_ui = ui.page_fluid(ui.layout_sidebar(
    ui.sidebar(
        ui.input_selectize(  
            "select",  
            "証券コード",  
            {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"},  
        ),
        ui.input_selectize(
            "fruits",
            "企業名",
            ["トヨタ", "任天堂", "Grape", "Orange", "Peach", "Pineapple", "Plum", "Strawberry"],
            multiple=False,
        ),
        ui.input_action_button("compare_search_btn", "検索"),
        ui.hr(),
        ui.input_action_button("btn1", "企業概要"),
        ui.input_action_button("btn2", "財務情報"),
        ui.input_action_button("btn3", "株価情報"),
    ),
    ui.output_ui("main_tab_content")
))
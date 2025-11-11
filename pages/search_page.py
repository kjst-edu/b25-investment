from shiny import ui, render, reactive

search_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(  
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
        ui.navset_pill_list(
            ui.nav_panel("企業概要", "Panel A content"),
            ui.nav_panel("財務情報", "Panel B content"),
            ui.nav_panel("C", "Panel C content"),
            id="tab_vertical",  
        )  
    ),
    "Main content",
)
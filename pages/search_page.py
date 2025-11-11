from shiny import ui, render, reactive

search_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_select(  
            "select",  
            "証券コード",  
            {"1A": "Choice 1A", "1B": "Choice 1B", "1C": "Choice 1C"},  
        ),
        ui.input_select(  
            "select",  
            "企業名",  
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
        ui.navset_tab(  
            ui.nav_panel("A", "Panel A content"),
            ui.nav_panel("B", "Panel B content"),
            ui.nav_panel("C", "Panel C content"),
            ui.nav_menu(
                "Other links",
                ui.nav_panel("D", "Panel D content"),
                "----",
                "Description:",
                ui.nav_control(
                    ui.a("Shiny", href="https://shiny.posit.co", target="_blank")
                ),
            ),
            id="tab",  
        )  
    ),
    "Main content",
)
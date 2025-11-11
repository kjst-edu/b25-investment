from shiny import ui, render, reactive

compare_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text("compare_search", "検索ワード", placeholder="キーワードを入力"),
        ui.input_action_button("compare_search_btn", "検索"),
        ui.hr(),
        ui.tags.p("サイドバー内に他のフィルタも置けます")
    ),
    "Main content",
)
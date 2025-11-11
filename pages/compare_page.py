from shiny import App, ui, reactive, render

companies = ["Company A", "Company B", "Company C"]

compare_ui = ui.layout_sidebar(
    ui.sidebar(
        ui.h3("企業間比較"),
        ui.p("比較する企業を選択してください（複数選択可能):", style="margin-bottom: 8px; font-weight: bold;"),
        ui.input_selectize(
            "selected_companies",
            "",
            choices=companies,
            selected=None,
            multiple=True,
            options={
                "placeholder": "企業を選択...",
                "maxItems": 5
            }
        )
    )
)
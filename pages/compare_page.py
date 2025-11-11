from shiny import ui

<<<<<<< HEAD
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
=======
compare_ui = ui.nav_panel(
    "比較",
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("企業間比較"),
            ui.p("比較する企業を選択してください（複数選択可）：",
                 style="margin-bottom: 8px; font-weight: 600;"),

            ui.input_selectize(
                "selected_companies",    
                "",                       
                choices=[],                
                selected=None,
                multiple=True,
                options={                  
                    "placeholder": "企業を選択...",
                    "maxItems": 3
                },
            ),
        ),
    ),
>>>>>>> 4e994a914e92571e8de2ebd9c9e8ec85da622c15
)
# %%
from shiny import App, ui, reactive, render
from pages.search_page import search_ui
from pages.compare_page import compare_ui
from server.search_logic import search_logic
from server.app_logic import compare_logic

app_ui = ui.page_navbar(
        ui.nav_panel("検索", search_ui),
        ui.nav_panel("比較", compare_ui),
        title="タイトル",
        id="page",
    )

def server(input, output, session):
    search_logic(input, output, session)
    compare_logic(input, output, session)

app = App(app_ui, server)

# %%

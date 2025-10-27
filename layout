# %%
from shiny import App, ui, reactive, render

app_ui = ui.page_navbar(
    ui.nav_panel("検索", "Page A content"),
    ui.nav_panel("比較", "Page B content"),
    title = "タイトル",
    id = "page",
)


def server(input, output, session):
    pass

app = App(app_ui, server)

# %%

from shiny import reactive, render, ui

def ui_content(input, output, session):
    # Plotly でチャートを作るなど
    return ui.HTML("<h3>株価・投資指標をここに表示</h3>")
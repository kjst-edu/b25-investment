from shiny import reactive, render, ui

def ui_content(input, output, session):
    # ここに財務情報の UI を書く
    return ui.HTML("<h3>財務情報をここに表示</h3>")
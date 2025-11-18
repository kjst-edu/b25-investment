from shiny import render, ui

def compare_logic(input, output, session):

    # カテゴリごとの指標リスト
    metric_choices = {
        "profit": {
            "sales": "売上高",
            "op_ptofit": "営業利益",
            "op_margin": "営業利益率",
            "roe": "ROE",
            "roa": "ROA",
        },
        "safety": {
            "equity_ratio": "自己資本比率",
            "current_ratio": "流動比率",
            "fixed_ratio": "固定比率",
        },
        "growth": {
            "sales_growth": "売上高成長率",
            "op_profit_growth": "営業利益成長率",
            "rd_ratio": "研究開発費率",
        },
        "stock": {
            "market_cap": "時価総額",
            "per": "PER",
            "pbr": "PBR",
            "div_yield": "配当利回り",
            "payout_ratio": "配当性向", 
        },
    }

    # チェックボックス
    @output
    @render.ui
    def metric_checkbox_ui():
        category = input.metric_category()
        choices = metric_choices.get(category, {})

        return ui.input_checkbox_group(
            "selected_metrics_for_table",
            None,
            choices=choices,
            selected=list(choices.keys())[:2]
        )
    
    # グラフ指標（選んだ中から1つ）
    @output
    @render.ui
    def metric_graph_ui():
        selected = input.selected_metrics_for_table() or []
        category = input.metric_category()
        choices_all = metric_choices.get(category, {})

        # 表で選んだ指標だけフィルタ
        choices_graph = {
            key: choices_all[key]
            for key in selected if key in choices_all
        }

        if not choices_graph:
            return ui.p("指標を選んでください。")
        
        return ui.input_radio_buttons(
            "selected_metric_for_graph",
            None,
            choices_graph,
            selected=selected[0],
        )
from shiny import ui


companies = ["Company A", "Company B", "Company C"]

industry_choices = {
    "it": "情報・通信",
    "electronics": "電気・電子",
    "auto": "自動車・輸送機器",
    "energy": "資源・エネルギー",
    "manufacturing": "製造業",
    "finance": "金融",
    "real_estate": "不動産",
    "services": "小売・サービス",
    "telecom": "通信キャリア",
    "infrastructure": "公共・インフラ",
}

compare_ui = ui.layout_sidebar(
    #----------左：サイドバー----------
    ui.sidebar(

        # 業界
        ui.h5("業界"),
        ui.input_select(
            "selected_industry",
            None,
            choices=industry_choices,
        ),

        # 企業
        ui.h5("企業（最大3社）"),
        ui.input_selectize(
            "selected_companies",
            None,
            choices=companies,
            multiple=True,
            options={
                "placeholder": "企業を選択...",
                "maxItems": 3,
            },
        ),
        
        ui.hr(),

        # 指標カテゴリ
        ui.h5("指標カテゴリ"),
        ui.input_radio_buttons(
            "metric_category",
            None,
            {
                "profit": "収益性",
                "safety": "安全性",
                "growth": "成長性",
                "stock": "株価",
            },
            selected="profit",
        ),

        ui.hr(),

        # 比較表に表示する指標（カテゴリに応じて変更）
        ui.h5("表に表示する指標"),
        ui.output_ui("metric_checkbox_ui"),

        # グラフに表示する指標（上で選んだ中から1つ）
        ui.h5("グラフに表示する指標"),
        ui.output_ui("metric_graph_ui"),

        ui.input_action_button(
            "run_compare", 
            "比較する",
            class_="btn-primary"),
    ),

    #----------右：メイン画面----------
    ui.page_fluid(
        ui.card(
            ui.h4("比較表"),
            ui.output_table("cmp_table"),
        ),
        ui.card(
            ui.h4("比較グラフ"),
            ui.layout_columns(
                ui.card(
                    ui.h5("最新年度"),
                    ui.output_plot("cmp_graph_latest"),
                ),
                ui.card(
                    ui.h5("時系列（5年）"),
                    ui.output_plot("cmp_graph_timeseries"),
                ),
            ),
        )
    )
)
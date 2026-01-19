from shiny import ui
from shinywidgets import output_widget


# 17業種
industry_choices = {
    "food": "食品",
    "it_services": "情報通信・サービスその他",
    "electronics_precision": "電機・精密",
    "retail": "小売",
    "materials_chemicals": "素材・化学",
    "construction_materials": "建設・資材",
    "trading_wholesale": "商社・卸売",
    "machinery": "機械",
    "auto_transport": "自動車・輸送機",
    "transport_logistics": "運輸・物流",
    "real_estate": "不動産",
    "finance_nonbank": "金融（除く銀行）",
    "banks": "銀行",
    "steel_nonferrous": "鉄鋼・非鉄",
    "pharma": "医薬品",
    "utilities_gas": "電力・ガス",
    "energy_resources": "エネルギー資源",
}

industry_choices_with_all = {"": "全業界"} | industry_choices


compare_ui = ui.layout_sidebar(
    #----------左：サイドバー----------
    ui.sidebar(
        ui.tags.style("""
            .metric-label-wrap { display:inline-flex; align-items:center; gap:6px; }
            .help-badge{
                display:inline-flex;
                align-items:center;
                justify-content:center;
                width:18px;
                height:18px;
                border-radius:50%;
                background:#0d6efd;  
                color:#fff;
                font-size:12px;
                font-weight:700;
                cursor: help;
                line-height:1;
                user-select:none;
            }
        """),
        ui.tags.script("""
            function initTooltips(){
              if (typeof bootstrap === "undefined") return;
              document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
                if (!el._tooltip) el._tooltip = new bootstrap.Tooltip(el);
              });
            }
            document.addEventListener("DOMContentLoaded", initTooltips);
            setInterval(initTooltips, 800);
        """),

        # 業界
        ui.h5("業界"),
        ui.input_select(
            "selected_industry",
            None,
            choices=industry_choices_with_all,
            selected="",
        ),

        # 企業
        ui.h5("企業（最大3社）"),
        ui.input_selectize(
            "selected_companies",
            None,
            choices={},
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
                "cashflow": "キャッシュフロー",
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
            class_="btn-outline-dark"),
    ),

    #----------右：メイン画面----------
    ui.page_fluid(
        ui.output_ui("compare_main_ui")
    )
)
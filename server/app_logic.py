from shiny import render, ui, reactive
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt
from server.data_loader import load_master_financials

INDUSTRY_KEY_TO_JP = {
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

MONEY_COLS = {
    "売上高(億円)", "営業利益(億円)", "当期純利益(億円)",
    "総資産(億円)", "自己資本(億円)", "流動資産(億円)", "流動負債(億円)",
    "固定資産(億円)", "負債総額(億円)",
    "営業CF(億円)", "投資CF(億円)", "財務CF(億円)", "フリーCF(億円)",
}

PERCENT_COLS = {
    "営業利益率", "ROE", "ROA", "自己資本比率", "流動比率",
    "営業CFマージン",
    "売上高成長率", "営業利益成長率", "当期純利益成長率",
}



# 表示フォーマット
def fmt_value(col: str, v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    if col in MONEY_COLS:
        return f"{v:,.1f}" 
    if col in PERCENT_COLS:
        return f"{v:.1f}%"
    if isinstance(v, (int, float)):
        return f"{v:,.2f}"
    return str(v)

# 比較表フォーマット
def fmt_value_table(col: str, v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return "—"
    if col in MONEY_COLS:
        return f"{v:,.1f}"
    if col in PERCENT_COLS:
        return f"{v:.1f}"   # ← %は付けない
    if isinstance(v, (int, float)):
        return f"{v:,.2f}"
    return str(v)

# グラフのY軸フォーマット
def format_yaxis(ax, col: str):
    if col in MONEY_COLS:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))
    elif col in PERCENT_COLS:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.0f}%"))



def compare_logic(input, output, session):
    # csvを読み込む
    df_all = load_master_financials()
    df_all["証券コード"] = df_all["証券コード"].astype(str)

    compare_ran = reactive.Value(False)

    @reactive.effect
    @reactive.event(input.run_compare)
    def _mark_compare_ran():
        compare_ran.set(True)

    # カテゴリごとの指標リスト
    metric_choices = {
        "profit": {
            "売上高(億円)": "売上高(億円)",
            "営業利益(億円)": "営業利益(億円)",
            "当期純利益(億円)": "当期純利益(億円)",
            "営業利益率": "営業利益率(%)",
            "ROE": "ROE(%)",
            "ROA": "ROA(%)",
        },
        "safety": {
            "自己資本比率": "自己資本比率(%)",
            "流動比率": "流動比率(%)",
        },
        "growth": {
            "売上高成長率": "売上高成長率(%)",
            "営業利益成長率": "営業利益成長率(%)",
            "当期純利益成長率": "当期純利益成長率(%)"
        },
        "cashflow": {
            "営業CF(億円)": "営業CF(億円)",
            "投資CF(億円)": "投資CF(億円)",
            "財務CF(億円)": "財務CF(億円)",
            "フリーCF(億円)": "フリーCF(億円)",
            "営業CFマージン": "営業CFマージン(%)",
        },
    }

    # 業界→企業候補の更新
    @reactive.effect
    def _update_company_choices():
        ind_key = input.selected_industry()
        if not ind_key:  
            sub = (
                df_all[["証券コード", "企業名"]]
                .drop_duplicates()
                .sort_values("証券コード")
            )
        else:
            jp = INDUSTRY_KEY_TO_JP.get(ind_key)
            if not jp:
                ui.update_selectize("selected_companies", choices={}, selected=[])
                return

            sub = (
                df_all[df_all["17業種区分"] == jp][["証券コード", "企業名"]]
                .drop_duplicates()
                .sort_values("証券コード")
            )

        choices = {str(r["証券コード"]): f'{r["企業名"]}【{str(r["証券コード"])}】' for _, r in sub.iterrows()}
        ui.update_selectize("selected_companies", choices=choices, selected=[])

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
    
    # 全社に共通する最新年度を優先する
    def latest_common_year(df_sub: pd.DataFrame, codes: list[str]) -> int:
        years_sets = []
        for code in codes:
            ys = set(df_sub[df_sub["証券コード"] == code]["年度"].dropna().astype(int).tolist())
            years_sets.append(ys)
        common = set.intersection(*years_sets) if years_sets else set()
        if common:
            return max(common)
        return int(df_sub["年度"].max())
    
    def build_company_labels(df_latest: pd.DataFrame, codes: list[str]) -> dict[str, str]:
        """
        表と同じルール：
        - 基本は企業名のみ
        - 企業名が重複した場合だけ（証券コード）を付ける
        戻り値: {コード: 表示名}
        """
        code_to_name = (
            df_latest[["証券コード", "企業名"]]
            .drop_duplicates()
            .set_index("証券コード")["企業名"]
            .to_dict()
        )

        names = [code_to_name.get(c, c) for c in codes]
        name_count = {}
        for n in names:
            name_count[n] = name_count.get(n, 0) + 1

        labels = {}
        for c, n in zip(codes, names):
            labels[c] = f"{n}（{c}）" if name_count[n] >= 2 else n
        return labels
    
    # 初期の右画面
    @output
    @render.ui
    def compare_main_ui():
        if not compare_ran.get():
            return ui.card(
                ui.h4("使い方"),
                ui.markdown(
                    """
    **1. 業界（任意）**  
    - 選択しない → 全企業から選べます  
    - 選択する → その業界の企業から選べます

    **2. 企業（最大3社）**  
    比較したい企業を選んでください。

    **3. 指標の選び方**  
    - 表：複数選択OK  
    - グラフ：表で選んだ中から1つだけ選択

    最後に **「比較する」** を押してください。
                    """
                ),
            )

        return ui.div(
            ui.card(
                ui.h4("比較表"),
                ui.output_ui("cmp_table"),  
            ),
            ui.card(
                ui.h4("比較グラフ"),
                ui.layout_columns(
                    ui.card(ui.output_ui("latest_year_header"), ui.output_plot("cmp_graph_latest")),
                    ui.card(ui.h5("時系列（3年）"), ui.output_plot("cmp_graph_timeseries")),
                    col_widths=[4, 8],
                ),
            ),
        )
    
    @output
    @render.ui
    @reactive.event(input.run_compare)
    def latest_year_header():
        codes = input.selected_companies() or []
        if not codes:
            return ui.h5("最新年度")

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            return ui.h5("最新年度")

        y = latest_common_year(df_sub, codes)
        return ui.h5(f"最新年度（{y}年）")
    
    # 企業比較表（最新年度）
    @output
    @render.ui
    @reactive.event(input.run_compare)
    def cmp_table():
        # 選択された企業と指標を取得
        codes = input.selected_companies() or []
        metric_cols = input.selected_metrics_for_table() or []

        if not codes or not metric_cols:
            return ui.p("企業と指標を選んでください。")

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            return ui.p("データがありません。")

        year = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == year].copy()

        code_to_name = (
            df_latest[["証券コード", "企業名"]]
            .drop_duplicates()
            .set_index("証券コード")["企業名"]
            .to_dict()
        )

        # 列名：企業名のみ（重複したらコードを付ける）
        names_in_order = [code_to_name.get(c, c) for c in codes]

        name_count = {}
        for name in names_in_order:
            name_count[name] = name_count.get(name, 0) + 1

        col_labels = {}
        for c, name in zip(codes, names_in_order):
            col_labels[c] = f"{name}（{c}）" if name_count[name] >= 2 else name

        category = input.metric_category()
        choices_all = metric_choices.get(category, {})
        metric_labels = [choices_all.get(m, m) for m in metric_cols]

        table = pd.DataFrame(index=metric_labels, columns=[col_labels[c] for c in codes], dtype=object)

        for c in codes:
            row_df = df_latest[df_latest["証券コード"] == c]
            if row_df.empty:
                continue
            row = row_df.iloc[0]
            for m, m_label in zip(metric_cols, metric_labels):
                table.loc[m_label, col_labels[c]] = fmt_value_table(m, row.get(m))

        df_show = table.reset_index().rename(columns={"index": f"指標（{year}年）"})
        
        html = df_show.to_html(index=False, classes="cmp-table", border=0)

        return ui.TagList(
            ui.tags.style("""
                .cmp-table { width:100%; table-layout:fixed; border-collapse:collapse; }
                .cmp-table th, .cmp-table td { padding:6px 10px; border-bottom:1px solid #eee; white-space:nowrap; }
                .cmp-table th { text-align:center; overflow:hidden; text-overflow:ellipsis; border-bottom:1px solid #ddd; }
                .cmp-table td:first-child { text-align:left; }
                .cmp-table td:not(:first-child) { text-align:right; font-variant-numeric: tabular-nums; }
                .cmp-table th:first-child, .cmp-table td:first-child { width:34%; }
                .cmp-table th, .cmp-table td { border-right: 1px solid #f0f0f0; }
                .cmp-table th:last-child, .cmp-table td:last-child { border-right: none; }
            """),
            ui.HTML(html)
        )
    
    # 企業比較グラフ（最新年度）
    @output
    @render.plot
    @reactive.event(input.run_compare)
    def cmp_graph_latest():
        codes = input.selected_companies() or []
        col = input.selected_metric_for_graph()

        if (not codes) or (col is None):
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "企業と指標を選択してください。", ha="center", va="center")
            ax.axis("off")
            return fig
        
        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "データがありません。", ha="center", va="center")
            ax.axis("off")
            return fig

        latest_year = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == latest_year].copy()

        label_map = build_company_labels(df_latest, codes)
        labels = [label_map[c] for c in codes]

        values = []
        for c in codes:
            row_df = df_latest[df_latest["証券コード"] == c]
            values.append(row_df.iloc[0][col] if not row_df.empty else float("nan"))

        fig, ax = plt.subplots(figsize=(5.2, 3.6))
        ax.bar(labels, values)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_title(col)
        ax.set_xlabel("企業")
        ax.set_ylabel(col)
        ax.tick_params(axis="x", rotation=20)

        format_yaxis(ax, col)

        for i, v in enumerate(values):
            if pd.isna(v):
                continue
            ax.text(i, v, fmt_value(col, v), ha="center", va="bottom", fontsize=8)

        ax.tick_params(axis="x", rotation=0)
        for t in ax.get_xticklabels():
            t.set_ha("right")

        fig.subplots_adjust(left=0.18, bottom=0.28, right=0.98, top=0.90)

        fig.tight_layout()
        return fig
    
    # 企業比較グラフ（時系列）
    @output
    @render.plot
    @reactive.event(input.run_compare)
    def cmp_graph_timeseries():
        codes = input.selected_companies() or []
        col = input.selected_metric_for_graph()

        if (not codes) or (col is None):
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "企業と指標を選択してください。", ha="center", va="center")
            ax.axis("off")
            return fig

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "データがありません。", ha="center", va="center")
            ax.axis("off")
            return fig

        fig, ax = plt.subplots()

        year = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == year].copy()
        label_map = build_company_labels(df_latest, codes)

        # 企業ごとに線を引く
        for c in codes:
            sub = df_sub[df_sub["証券コード"] == c].sort_values("年度")
            if sub.empty:
                continue
            name = sub["企業名"].iloc[0]
            ax.plot(sub["年度"], sub[col], marker="o", label=label_map.get(c, c))
            ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), borderaxespad=0)
            fig.subplots_adjust(right=0.78) 

        years = sorted(df_sub["年度"].unique())
        ax.set_xticks(years)
        ax.set_xticklabels([str(int(y)) for y in years])

        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_title(f"{col} の推移")
        ax.set_xlabel("年度")
        ax.set_ylabel(col)
        ax.legend()

        format_yaxis(ax, col)

        fig.tight_layout()

        return fig

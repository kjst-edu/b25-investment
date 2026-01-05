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
    "finance_nonbank": "金融（除く金融）",
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

# グラフのY軸フォーマット
def format_yaxis(ax, col: str):
    if col in MONEY_COLS:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:,.0f}"))
    elif col in PERCENT_COLS:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"{x:.0f}%"))



def compare_logic(input, output, session):
    # csvを読み込む
    df_all = load_master_financials()

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
            ui.update_selectize("selected_companies", choices={}, selected=[])
            return

        jp = INDUSTRY_KEY_TO_JP.get(ind_key)
        if not jp:
            ui.update_selectize("selected_companies", choices={}, selected=[])
            return

        sub = (
            df_all[df_all["17業種区分"] == jp][["証券コード", "企業名"]]
            .drop_duplicates()
            .sort_values("証券コード")
        )

        # value=証券コード, label="1301 極洋"
        choices = {r["証券コード"]: f'{r["証券コード"]} {r["企業名"]}' for _, r in sub.iterrows()}
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
    
    # 企業比較表（最新年度）
    @output
    @render.table
    @reactive.event(input.run_compare)
    def cmp_table():
        # 選択された企業と指標を取得
        codes = input.selected_companies() or []
        metric_cols = input.selected_metrics_for_table() or []

        if not codes or not metric_cols:
            return pd.DataFrame()

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            return pd.DataFrame()

        year = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == year].copy()

        code_to_name = (
            df_latest[["証券コード", "企業名"]]
            .drop_duplicates()
            .set_index("証券コード")["企業名"]
            .to_dict()
        )
        col_labels = {c: f"{c} {code_to_name.get(c, '')}".strip() for c in codes}

        table = pd.DataFrame(index=metric_cols, columns=[col_labels[c] for c in codes], dtype=object)

        for c in codes:
            row_df = df_latest[df_latest["証券コード"] == c]
            if row_df.empty:
                continue
            row = row_df.iloc[0]
            for col in metric_cols:
                table.loc[col, col_labels[c]] = fmt_value(col, row.get(col))

        df_show = table.reset_index().rename(columns={"index": f"指標（{year}年）"})
        return df_show
    
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

        code_to_name = (
            df_latest[["証券コード", "企業名"]]
            .drop_duplicates()
            .set_index("証券コード")["企業名"]
            .to_dict()
        )
        labels = [f"{c} {code_to_name.get(c, '')}".strip() for c in codes]

        values = []
        for c in codes:
            row_df = df_latest[df_latest["証券コード"] == c]
            values.append(row_df.iloc[0][col] if not row_df.empty else float("nan"))

        fig, ax = plt.subplots()
        ax.bar(labels, values)
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_title(f"{col}（{latest_year}年）")
        ax.set_xlabel("企業")
        ax.set_ylabel(col)
        ax.tick_params(axis="x", rotation=20)

        format_yaxis(ax, col)

        for i, v in enumerate(values):
            if pd.isna(v):
                continue
            ax.text(i, v, fmt_value(col, v), ha="center", va="bottom", fontsize=8)

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

        # 企業ごとに線を引く
        for c in codes:
            sub = df_sub[df_sub["証券コード"] == c].sort_values("年度")
            if sub.empty:
                continue
            name = sub["企業名"].iloc[0]
            ax.plot(sub["年度"], sub[col], marker="o", label=f"{c} {name}".strip())

        years = sorted(df_sub["年度"].unique())
        ax.set_xticks(years)
        ax.set_xticklabels([str(int(y)) for y in years])

        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.set_title(f"{col} の推移（時系列）")
        ax.set_xlabel("年度")
        ax.set_ylabel(col)
        ax.legend()

        format_yaxis(ax, col)

        fig.tight_layout()

        return fig

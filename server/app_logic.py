from shiny import render, ui, reactive
from matplotlib.ticker import FuncFormatter
import pandas as pd
import matplotlib.pyplot as plt
from server.data_loader import load_master_financials
import numpy as np
from matplotlib.patches import FancyBboxPatch
from shinywidgets import render_widget, output_widget
import plotly.graph_objects as go
from server.explanations import EXPLANATIONS



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

PLOT_COLORS = ["#636EFA", "#EF553B", "#00CC96"] 

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

    metric_choices_table = {
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
            "当期純利益成長率": "当期純利益成長率(%)",
        },
        "cashflow": {
            "営業CF(億円)": "営業CF(億円)",
            "投資CF(億円)": "投資CF(億円)",
            "財務CF(億円)": "財務CF(億円)",
            "フリーCF(億円)": "フリーCF(億円)",
            "営業CFマージン": "営業CFマージン(%)",
        },
    }

    METRIC_KEY_MAP = {
        "ROE": "roe",
        "自己資本比率": "equity_ratio",
        "売上高成長率": "revenue_growth",
        "営業利益成長率": "operating_income_growth",
        "当期純利益成長率": "net_income_growth",
        "営業CF(億円)": "operating_cf",
        "投資CF(億円)": "investing_cf",
        "財務CF(億円)": "financing_cf",
        "フリーCF(億円)": "free_cf",
        "営業CFマージン": "operating_cf_margin",
        "営業利益率": "operating_margin",
        "ROA": "roa",
        "流動比率": "current_ratio",
    }

    def get_help_text(metric_col: str) -> str:
        key = METRIC_KEY_MAP.get(metric_col)
        if not key:
            return ""   
        return EXPLANATIONS.get(key, "")

    def label_with_help(display_name: str, help_text: str):
        if not help_text:
            return display_name  

        safe = (
            help_text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        return ui.HTML(
            f"""
            <span class="metric-label-wrap">
            <span>{display_name}</span>
            <span class="help-badge" data-bs-toggle="tooltip" data-bs-placement="top" title="{safe}">?</span>
            </span>
            """
        )


    # カテゴリごとの指標リスト
    metric_choices = {
        "profit": {
            "売上高(億円)": label_with_help("売上高", get_help_text("売上高(億円)")),
            "営業利益(億円)": label_with_help("営業利益", get_help_text("営業利益(億円)")),
            "当期純利益(億円)": label_with_help("当期純利益", get_help_text("当期純利益(億円)")),
            "営業利益率": label_with_help("営業利益率", get_help_text("営業利益率")),
            "ROE": label_with_help("ROE", get_help_text("ROE")),
            "ROA": label_with_help("ROA", get_help_text("ROA")),
        },
        "safety": {
            "自己資本比率": label_with_help("自己資本比率", get_help_text("自己資本比率")),
            "流動比率": label_with_help("流動比率", get_help_text("流動比率")),
        },
        "growth": {
            "売上高成長率": label_with_help("売上高成長率", get_help_text("売上高成長率")),
            "営業利益成長率": label_with_help("営業利益成長率", get_help_text("営業利益成長率")),
            "当期純利益成長率": label_with_help("当期純利益成長率", get_help_text("当期純利益成長率")),
        },
        "cashflow": {
            "営業CF(億円)": label_with_help("営業CF", get_help_text("営業CF(億円)")),
            "投資CF(億円)": label_with_help("投資CF", get_help_text("投資CF(億円)")),
            "財務CF(億円)": label_with_help("財務CF", get_help_text("財務CF(億円)")),
            "フリーCF(億円)": label_with_help("フリーCF", get_help_text("フリーCF(億円)")),
            "営業CFマージン": label_with_help("営業CFマージン", get_help_text("営業CFマージン")),
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
    - 比較したい企業を選んでください。

    **3. 指標の選び方**  
    - 表：複数選択OK  
    - グラフ：表で選んだ指標の中から1つだけ選択

    最後に **「比較する」** を押してください。
                    """
                ),
            )

        return ui.div(
            ui.tags.style("""
                /* plotly の上のアイコン列（modebar）を消す */
                .js-plotly-plot .modebar-container { display: none !important; }
                .js-plotly-plot .modebar { display: none !important; }
            """),
            ui.card(
                ui.h4("比較表"),
                ui.output_ui("cmp_table"),  
            ),
            ui.card(
                ui.h4("比較グラフ"),
                ui.card(
                    ui.output_ui("latest_year_header"),
                    ui.output_plot("cmp_graph_latest"),
                ),
                ui.card(
                    ui.h5("時系列（3年）"),
                    ui.row(
                        ui.column(8, output_widget("cmp_graph_timeseries")),
                        ui.column(4, ui.output_ui("ts_info_boxes")),
                    ),
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
        choices_all = metric_choices_table.get(category, {})
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
        
        def _td_class(v):
            return "miss" if str(v) == "—" else ""

        styled = df_show.style.set_table_attributes('class="cmp-table"').applymap(
            lambda v: "text-align:center;" if str(v) == "—" else None,
            subset=df_show.columns[1:], 
        )
        td_classes = df_show.copy()
        for c in df_show.columns[1:]:
            td_classes[c] = df_show[c].map(_td_class)
        styled = styled.set_td_classes(td_classes)
        styled = styled.hide(axis="index")

        html = styled.to_html()

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
                .cmp-table td.miss { text-align:center !important; color:#666; }
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

        missing = [pd.isna(v) for v in values]
        plot_values = [0 if pd.isna(v) else v for v in values]

        x = np.arange(len(labels))

        fig, ax = plt.subplots(figsize=(8.0, 3.8))
        bars = ax.bar(x, plot_values)

        for b, miss in zip(bars, missing):
            if miss:
                b.set_alpha(0.0)
                b.set_linewidth(0.0)

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, ha="center")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.axhline(0, color="black", linewidth=1.2)
        ax.set_title(col)
        # ax.set_xlabel("企業")
        # ax.set_ylabel(col)

        format_yaxis(ax, col)

        vals = [v for v in values if not pd.isna(v)]
        if vals:
            ymin, ymax = min(vals), max(vals)
            span = ymax - ymin
            pad = (span * 0.08) if span > 0 else (abs(ymax) * 0.15 + 1)
            ax.set_ylim(ymin - pad, ymax + pad)

        for b, v, miss in zip(bars, values, missing):

            cx = b.get_x() + b.get_width() / 2

            if miss:
                ax.annotate(
                    "データなし",
                    xy=(cx, 0),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#666",
                )
                continue

            if v >= 0:
                va = "bottom"           
                offset = 1          
            else:
                va = "top"       
                offset = -1           

            ax.annotate(
                fmt_value(col, v),
                xy=(cx, v),
                xytext=(0, offset),
                textcoords="offset points",
                ha="center",
                va=va,
                fontsize=8,
                clip_on=False,
            )


        fig.subplots_adjust(left=0.18, bottom=0.28, right=0.98, top=0.90)
        fig.tight_layout()
        return fig

    # 企業比較グラフ（時系列）
    @output
    @render_widget
    @reactive.event(input.run_compare)
    def cmp_graph_timeseries():
        codes = input.selected_companies() or []
        col = input.selected_metric_for_graph()

        if (not codes) or (col is None):
            fig = go.Figure()
            fig.add_annotation(text="企業と指標を選択してください。", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=380)
            return fig

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            fig = go.Figure()
            fig.add_annotation(text="データがありません。", x=0.5, y=0.5, showarrow=False)
            fig.update_layout(height=380)
            return fig

        years = sorted(df_sub["年度"].dropna().astype(int).unique().tolist())

        # ラベル
        year_latest = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == year_latest].copy()
        label_map = build_company_labels(df_latest, codes)

        def hover_fmt(c: str, v) -> str:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return "欠損"
            return fmt_value(c, float(v))

        fig = go.Figure()

        for i, code in enumerate(codes):
            sub = df_sub[df_sub["証券コード"] == code].set_index("年度")
            s = sub[col].reindex(years)

            yvals = [None if (v is None or (isinstance(v, float) and pd.isna(v))) else float(v) for v in s.values]
            hover_text = [hover_fmt(col, v) for v in s.values]

            label = label_map.get(code, code)

            color = PLOT_COLORS[i % len(PLOT_COLORS)]

            fig.add_trace(
                go.Scatter(
                    x=years,
                    y=yvals,
                    mode="lines+markers",
                    name=label,
                    line=dict(color=color, width=2),
                    marker=dict(color=color, size=7),
                    text=hover_text,
                    hovertemplate="%{text}<extra></extra>",
                    connectgaps=False,
                )
            )

        # 軸フォーマット
        yaxis = {}
        if col in MONEY_COLS:
            yaxis.update(tickformat=",")
        elif col in PERCENT_COLS:
            yaxis.update(ticksuffix="%", tickformat=".0f")

        fig.update_layout(
            title=f"{col} の推移",
            height=380,
            margin=dict(l=50, r=20, t=60, b=50),
            hovermode="closest",
            showlegend=False,
        )
        fig.update_layout(dragmode=False)
        fig.update_layout(hoverlabel=dict(font=dict(color="white")))
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)

        fig.update_xaxes(type="category", categoryorder="array", categoryarray=years)
        fig.update_yaxes(**yaxis)

        fig.add_hline(y=0, line_width=1, line_dash="dash", opacity=0.6)
       
        return fig
    
    # 情報カード
    @output
    @render.ui
    @reactive.event(input.run_compare)
    def ts_info_boxes():
        codes = input.selected_companies() or []
        col = input.selected_metric_for_graph()

        if (not codes) or (col is None):
            return ui.p("")

        df_sub = df_all[df_all["証券コード"].isin(codes)].copy()
        if df_sub.empty:
            return ui.p("")

        years = sorted(df_sub["年度"].dropna().astype(int).unique().tolist())

        # ラベル
        year_latest = latest_common_year(df_sub, codes)
        df_latest = df_sub[df_sub["年度"] == year_latest].copy()
        label_map = build_company_labels(df_latest, codes)

        def unit_suffix(c: str) -> str:
            if c in MONEY_COLS:
                return "億円"
            if c in PERCENT_COLS:
                return "%"
            return ""

        u = unit_suffix(col)

        def fmt_delta(c: str, v: float) -> str:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return "—"
            if c in MONEY_COLS:
                return f"{v:+,.1f} {u}".strip()
            if c in PERCENT_COLS:
                return f"{v:+.1f}%"
            return f"{v:+,.2f}"

        def fmt_avg(c: str, v: float) -> str:
            if v is None or (isinstance(v, float) and pd.isna(v)):
                return "—"
            if c in MONEY_COLS:
                return f"{v:,.1f} {u}".strip()
            if c in PERCENT_COLS:
                return f"{v:.1f}%"
            return f"{v:,.2f}"

        cards = []
        for i, c in enumerate(codes):
            sub = df_sub[df_sub["証券コード"] == c].set_index("年度")
            s = sub[col].reindex(years)

            color = PLOT_COLORS[i % len(PLOT_COLORS)]

            label_raw = str(label_map.get(c, c))
            max_chars = 14
            label = label_raw if len(label_raw) <= max_chars else label_raw[:max_chars-1] + "…"

            miss_years = [str(int(y)) for y in years if pd.isna(s.loc[y])]
            s_non = s.dropna()

            if not s_non.empty:
                avg = float(s_non.mean())

                if len(s_non) >= 2:
                    first_y, last_y = int(s_non.index[0]), int(s_non.index[-1])
                    delta = float(s_non.iloc[-1] - s_non.iloc[0])
                    delta_text = f"変化: {fmt_delta(col, delta)}（{first_y}→{last_y}）"
                else:
                    delta_text = "変化: —（データ1点）"

                avg_text = f"平均: {fmt_avg(col, avg)}"
                miss_text = ("欠損: " + ",".join(miss_years)) if miss_years else ""
            else:
                avg_text = "平均: —"
                delta_text = "変化: —"
                miss_text = "欠損（全期間）"

            cards.append(
                ui.tags.div(
                    ui.tags.div(
                        ui.tags.span(
                            style=f"""
                                display:inline-block;
                                width:26px;
                                height:3px;
                                background:{color};
                                border-radius:2px;
                                margin-right:8px;
                                flex: 0 0 auto;  
                            """
                        ),
                        ui.tags.span(
                            label, 
                            style="""
                                font-weight:600;
                                flex: 1 1 auto; 
                                min-width: 0;
                                white-space:nowrap;
                                overflow: hidden;
                                text-overflow:ellipsis;
                            """,
                        ),
                        style="""
                            margin-bottom:6px;
                            display:flex;
                            align-items:center;
                            gap: 0px;
                        """,
                    ),
                    ui.tags.div(avg_text, style="font-size:12px; color:#555; margin-bottom:2px;"),
                    ui.tags.div(delta_text, style="font-size:12px; color:#555; margin-bottom:2px;"),
                    ui.tags.div(miss_text, style="font-size:12px; color:#777;") if miss_text else ui.tags.div(),
                    style="""
                        border:1px solid #ddd;
                        border-radius:10px;
                        padding:10px 12px;
                        margin-bottom:10px;
                        background:#fff;
                    """,
                )
            )

        return ui.TagList(*cards)


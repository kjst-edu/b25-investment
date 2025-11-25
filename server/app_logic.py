from shiny import render, ui
import pandas as pd

def create_mock_financials() -> pd.DataFrame:

    #Company A〜C の 2019〜2023 年の仮データ。

    companies = ["Company A", "Company B", "Company C"]
    years = [2019, 2020, 2021, 2022, 2023]

    base_sales = {"Company A": 1000, "Company B": 800, "Company C": 600}
    base_margin = {"Company A": 0.10, "Company B": 0.08, "Company C": 0.12}
    base_equity_ratio = {"Company A": 40, "Company B": 35, "Company C": 45}
    base_current_ratio = {"Company A": 150, "Company B": 130, "Company C": 160}
    base_fixed_ratio = {"Company A": 60, "Company B": 55, "Company C": 50}
    base_roe = {"Company A": 8, "Company B": 7, "Company C": 9}
    base_roa = {"Company A": 4, "Company B": 3.5, "Company C": 4.5}
    base_mcap = {"Company A": 2000, "Company B": 1500, "Company C": 1200}

    rows = []

    for company in companies:
        prev_sales = None
        prev_op_profit = None

        for i, year in enumerate(years):
            # 会社ごとに成長率を少し変える
            if company == "Company A":
                growth_factor = 1 + 0.04 * i
            elif company == "Company B":
                growth_factor = 1 + 0.03 * i
            else:
                growth_factor = 1 + 0.05 * i

            sales = round(base_sales[company] * growth_factor, 1)
            margin = base_margin[company] + 0.005 * i
            op_profit = round(sales * margin, 1)

            # 成長率（最初の年は None）
            if prev_sales is None:
                sales_growth = None
                op_profit_growth = None
            else:
                sales_growth = round((sales - prev_sales) / prev_sales * 100, 1)
                op_profit_growth = round(
                    (op_profit - prev_op_profit) / prev_op_profit * 100, 1
                )

            prev_sales = sales
            prev_op_profit = op_profit

            equity_ratio = base_equity_ratio[company] + i * 0.5
            current_ratio = base_current_ratio[company] + i * 2
            fixed_ratio = base_fixed_ratio[company] - i * 1
            roe = base_roe[company] + i * 0.2
            roa = base_roa[company] + i * 0.1
            rd_ratio = 5.0 + i * 0.2

            market_cap = round(base_mcap[company] * growth_factor * 1.1, 1)
            if company == "Company A":
                per = 15 + i
                pbr = 1.2 + 0.05 * i
                div_yield = 2.0 + 0.1 * i
                payout_ratio = 30 + i
            elif company == "Company B":
                per = 13 + i
                pbr = 1.1 + 0.04 * i
                div_yield = 2.3 + 0.1 * i
                payout_ratio = 35 + i
            else:
                per = 17 + i
                pbr = 1.4 + 0.03 * i
                div_yield = 1.8 + 0.1 * i
                payout_ratio = 25 + i

            rows.append(
                {
                    "company": company,
                    "fiscal_year": year,
                    # 収益性
                    "sales": sales,
                    "op_ptofit": op_profit,      # ★ metric_choices と同じキー名
                    "op_margin": margin * 100,   # % 表示想定
                    "roe": roe,
                    "roa": roa,
                    # 安全性
                    "equity_ratio": equity_ratio,
                    "current_ratio": current_ratio,
                    "fixed_ratio": fixed_ratio,
                    # 成長性
                    "sales_growth": sales_growth,
                    "op_profit_growth": op_profit_growth,
                    "rd_ratio": rd_ratio,
                    # 株価
                    "market_cap": market_cap,
                    "per": per,
                    "pbr": pbr,
                    "div_yield": div_yield,
                    "payout_ratio": payout_ratio,
                }
            )

    return pd.DataFrame(rows)



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
    
    # 企業比較表
    @output
    @render.table
    def cmp_table():
        # 選択された企業と指標を取得
        companies = input.selected_companies() or []
        metric_keys = input.selected_metrics_for_table() or []

        if not companies or not metric_keys:
            return pd.DataFrame()

        # 仮データを取得
        df_fin = create_mock_financials()

        df_fin = df_fin[df_fin["company"].isin(companies)]
        
        # 最新年度のみを抽出
        latest_year = df_fin["fiscal_year"].max()
        df_latest = df_fin[df_fin["fiscal_year"] == latest_year]

        # 表の作成
        table = pd.DataFrame(index=metric_keys, columns=companies, dtype="float")

        for c in companies:
            sub = df_latest[df_latest["company"] == c]
            if sub.empty:
                continue
            row = sub.iloc[0]
            for m in metric_keys:
                if m in row.index:
                    table.loc[m, c] = row[m]

        # 行名を日本語ラベルに変換
        category = input.metric_category()
        label_map = metric_choices.get(category, {})
        table.index = [label_map.get(k, k) for k in table.index]

        df_show = table.reset_index().rename(columns={"index": "指標"})

        # 全て左寄せ
        styled = (
            df_show.style
            .hide(axis="index")
            .set_table_styles(
                [
                    {"selector": "th", "props": [("text-align", "left")]},
                    {"selector": "td", "props": [("text-align", "left")]},
                ]
            )
        )

        return styled



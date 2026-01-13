from shiny import App, Inputs, Outputs, Session, reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
import os
from datetime import datetime, timedelta
from server.explanations import EXPLANATIONS
from server.data_company_to_code import CODE_TO_COMPANY, COMPANY_TO_CODE, CODE_TO_INDUSTRY, INDUSTRY_TO_CODES

def ui_content(input, output, session):

    @render.text
    def company_name():
        # select_codeの値を直接使用
        code = input.select_code() if input.select_code() else ""
        company = CODE_TO_COMPANY.get(code, "企業を選択してください")
        return company

    @reactive.calc
    def ticker():
        code = input.select_code()
        if code:
            return yf.Ticker(code)
        return None
    
    @reactive.calc
    def csv_financial_data():
        """CSVから財務データを取得"""
        code = input.select_code()
        if not code:
            return None
        
        try:
            if os.path.exists('master_financial_indicators.csv'):
                df = pd.read_csv('master_financial_indicators.csv')
                
                # 証券コードから .T を除去
                clean_code = code.replace('.T', '') if code.endswith('.T') else code
                
                # 証券コードでフィルタリング
                company_data = df[df['証券コード'] == int(clean_code)]
                
                if not company_data.empty:
                    # 2024年度データを優先的に取得
                    year_2024_data = company_data[company_data['年度'] == 2024]
                    if not year_2024_data.empty:
                        latest_data = year_2024_data.iloc[0]
                        return {
                            'roe': latest_data.get('ROE', None),
                            'equity_ratio': latest_data.get('自己資本比率', None),
                            'data_source': '2024年度データ'
                        }
            
            return None
            
        except Exception as e:
            return None

    @render.ui
    def price():
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            price = info.get("currentPrice")
            prev = info.get("previousClose")

            if not price or not prev:
                return "―"

            change = price - prev
            change_percent = (change / prev) * 100
            sign = "+" if change >= 0 else "−"
            color = "red" if change >= 0 else "blue"

            return ui.HTML(
                f'<span style="font-size:30px;">{price:,.0f}'
                f'<span style="font-size:13px;"> 円</span></span> '
                f'<span style="font-size:13px;"> 前日比</span> '
                f'<span style="color:{color}; font-size:13px; margin-left:4px;">'
                f'({sign}{abs(change):,.0f} 円 / {sign}{abs(change_percent):.2f}%)'
                f'</span>'
            )
        except:
            return "データ取得エラー"
    
    @render.ui
    def market_cap():
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            mc = info.get("marketCap")
            
            if not mc:
                return "―"

            mc_oku = mc / 100_000_000

            return ui.HTML(
                f'<div style="font-size:28px;">{mc_oku:,.1f}'
                f'<span style="font-size:13px;"> </span></div>'
                f'<div style="text-align:right; font-size:13px;">億円</div>'
            )
        except:
            return "―"
    
    @render.ui
    def per():
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            per = info.get("trailingPE")
            return f"{per:.2f}" if per else "―"
        except:
            return "―"
    
    @render.ui
    def roe():
        # まずCSVデータを確認
        csv_data = csv_financial_data()
        
        if csv_data and csv_data.get('roe') is not None:
            roe_value = csv_data['roe']
            return f"{roe_value:.1f}%"
        
        # CSVにデータがない場合、Yahoo Financeから取得
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            roe_yf = info.get("returnOnEquity")
            return f"{roe_yf*100:.1f}%" if roe_yf else "―"
        except:
            return "―"
    
    @render.ui
    def equity_ratio():
        # まずCSVデータを確認
        csv_data = csv_financial_data()
        
        if csv_data and csv_data.get('equity_ratio') is not None:
            equity_value = csv_data['equity_ratio']
            return f"{equity_value:.1f}%"
        
        # CSVにデータがない場合、Yahoo Financeから取得
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            debt_to_equity = info.get("debtToEquity")
            if debt_to_equity:
                ratio = 100 / (1 + debt_to_equity)
                return f"{ratio:.1f}%"
            else:
                return "―"
        except:
            return "―"
    
    @render.ui
    def dividend_yield():
        t = ticker()
        if not t:
            return "―"
            
        try:
            info = t.info
            dividend = info.get("dividendYield")
            return f"{dividend:.2f}%" if dividend else "―"
        except:
            return "―"
    
    # 売上グラフを追加（10年分）
    @render.plot
    def revenue_chart():
        t = ticker()
        if not t:
            return
            
        try:
            # 年次財務データを取得
            financials = t.financials
            
            if financials.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '売上データが取得できませんでした', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=16)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                return fig
            
            # 売上データを探す（複数のキーを試す）
            revenue_keys = ['Total Revenue', 'Revenue', 'Net Sales', 'Sales']
            revenue_data = None
            
            for key in revenue_keys:
                if key in financials.index:
                    revenue_data = financials.loc[key]
                    break
            
            if revenue_data is not None and not revenue_data.empty:
                # NaN値を除去
                revenue_data = revenue_data.dropna()
                
                if revenue_data.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.text(0.5, 0.5, '有効な売上データがありません', 
                        ha='center', va='center', transform=ax.transAxes, fontsize=16)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    return fig
                
                # データを年度順にソート
                revenue_data = revenue_data.sort_index()
                
                # 最新の10年分のデータを取得
                if len(revenue_data) > 10:
                    revenue_data = revenue_data.tail(10)
                
                # 単位を億円に変換
                revenue_oku = revenue_data / 100_000_000
                
                # 無限大や非常に大きな値をチェック
                revenue_oku = revenue_oku.replace([float('inf'), float('-inf')], None).dropna()
                
                if revenue_oku.empty or len(revenue_oku) == 0:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.text(0.5, 0.5, '表示可能な売上データがありません', 
                        ha='center', va='center', transform=ax.transAxes, fontsize=16)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    return fig
                
                # グラフを作成
                fig, ax = plt.subplots(figsize=(12, 6))
                
                # 棒グラフを作成
                bars = ax.bar(range(len(revenue_oku)), revenue_oku.values, 
                            color='steelblue', alpha=0.7, edgecolor='darkblue', linewidth=1)
                
                # 年度ラベルを設定
                years = [date.year for date in revenue_oku.index]
                ax.set_xticks(range(len(revenue_oku)))
                ax.set_xticklabels(years, rotation=0)
                
                # ラベルとタイトル
                ax.set_ylabel('売上高 (億円)', fontsize=12)
                
                # Y軸の範囲を安全に設定
                max_val = max(revenue_oku.values)
                ax.set_ylim(0, max_val * 1.1)
                
                # グリッドを追加
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                ax.set_axisbelow(True)
                
                # 数値ラベルを棒グラフの上に追加
                for bar, value in zip(bars, revenue_oku.values):
                    if not pd.isna(value) and value != float('inf'):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{value:,.0f}', ha='center', va='bottom', 
                            fontsize=10, fontweight='bold')
                
                # レイアウトを調整
                plt.tight_layout()
                return fig
            
            else:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '売上データが見つかりませんでした', 
                    ha='center', va='center', transform=ax.transAxes, fontsize=16)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                return fig
                
        except Exception as e:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'グラフの作成に失敗しました\n{str(e)}', 
                ha='center', va='center', transform=ax.transAxes, fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            return fig
    
    company_info_2 = ui.TagList(
        ui.div(
            ui.h2(ui.output_text("company_name"), style="text-align: center; margin-bottom: 20px; color: #333;"),
            style="margin-bottom: 15px;"
        ),
        ui.layout_columns(
            ui.value_box("現在の株価", ui.output_ui("price")),
            ui.value_box("時価総額", ui.output_ui("market_cap")),
            ui.value_box(
                ui.tooltip(
                    ui.span("PER ", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                    EXPLANATIONS["per"]
                ),
                ui.output_ui("per")
            ),
            ui.value_box(
                ui.tooltip(
                    ui.span("ROE ", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                    EXPLANATIONS["roe"]
                ),
                ui.output_ui("roe")
            ),
            ui.value_box(
                ui.tooltip(
                    ui.span("自己資本比率 ", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                    EXPLANATIONS["equity_ratio"]
                ),
                ui.output_ui("equity_ratio")
            ),
            ui.value_box("配当利回り", ui.output_ui("dividend_yield")),
            fill=False,
        ),
        # 売上グラフを追加
        ui.card(
            ui.card_header("売上高推移"),
            ui.output_plot("revenue_chart")
        ),
    )
    return company_info_2
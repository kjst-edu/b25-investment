from shiny import reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd
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
    def financial_data():
        """財務データを取得して収益性指標を計算"""
        code = input.select_code()
        if not code:
            return None
        
        try:
            # まず、master_financial_indicators.csvからデータを取得
            df = pd.read_csv('master_financial_indicators_v2.csv')
            
            # 証券コードでフィルタリング
            code = int(code.replace('.T', ''))
            company_data = df[df['証券コード'] == int(code)]
            
            # データソースと年度を追跡
            data_source = None
            year = None
            
            # 2024年度データから優先的に取得
            for target_year in [2024, 2023, 2022]:
                year_data = company_data[company_data['年度'] == target_year]
                if not year_data.empty:
                    latest_data = year_data.iloc[0]
                    data_source = f"{target_year}年度時点"
                    year = str(target_year)
                    
                    return {
                        'operating_margin': latest_data.get('営業利益率', None),
                        'roe': latest_data.get('ROE', None),
                        'roa': latest_data.get('ROA', None),
                        'equity_ratio': latest_data.get('自己資本比率', None),
                        'current_ratio': latest_data.get('流動比率', None),
                        'fixed_ratio': latest_data.get('固定比率', None),  # CSVにない場合はNone
                        'revenue_growth': latest_data.get('売上高成長率', None),
                        'operating_income_growth': latest_data.get('営業利益成長率', None),
                        'eps': None,  # CSVにない場合はNone
                        'operating_cf': latest_data.get('営業CF(億円)', None),
                        'investing_cf': latest_data.get('投資CF(億円)', None),
                        'financing_cf': latest_data.get('財務CF(億円)', None),
                        'free_cf': latest_data.get('フリーCF(億円)', None),
                        'data_source': data_source,
                        'year': year
                    }
            
            # CSVにデータがない場合、Yahoo Financeから取得
            ticker_obj = ticker()
            if not ticker_obj:
                return None
            
            # 財務諸表データを取得
            financials = ticker_obj.financials
            balance_sheet = ticker_obj.balance_sheet
            cash_flow = ticker_obj.cashflow
            
            if financials.empty or balance_sheet.empty:
                return None
            
            # 最新年度とその前年度のデータを取得（成長率計算のため）
            latest_year = financials.columns[0]
            prev_year = financials.columns[1] if len(financials.columns) > 1 else None
            
            # === 基本財務データ取得 ===
            # 売上高（Revenue/Total Revenue）
            revenue_keys = ['Total Revenue', 'Revenue']
            revenue = None
            prev_revenue = None
            for key in revenue_keys:
                if key in financials.index:
                    revenue = financials.loc[key, latest_year]
                    if prev_year is not None:
                        prev_revenue = financials.loc[key, prev_year]
                    break
            
            # 営業利益（Operating Income）
            operating_income_keys = ['Operating Income', 'EBIT']
            operating_income = None
            prev_operating_income = None
            for key in operating_income_keys:
                if key in financials.index:
                    operating_income = financials.loc[key, latest_year]
                    if prev_year is not None:
                        prev_operating_income = financials.loc[key, prev_year]
                    break
            
            # 純利益（Net Income）
            net_income_keys = ['Net Income', 'Net Income Common Stockholders']
            net_income = None
            for key in net_income_keys:
                if key in financials.index:
                    net_income = financials.loc[key, latest_year]
                    break
            
            # EPS（基本的に株式数で純利益を割って算出、またはyfinanceから直接取得）
            eps = None
            try:
                # yfinanceの情報から取得を試行
                info = ticker_obj.info
                eps = info.get('trailingEps', None)
            except:
                pass
            
            # 総資産（Total Assets）
            total_assets_keys = ['Total Assets']
            total_assets = None
            for key in total_assets_keys:
                if key in balance_sheet.index:
                    total_assets = balance_sheet.loc[key, latest_year]
                    break
            
            # 株主資本（Stockholders Equity）
            equity_keys = ['Stockholders Equity', 'Total Stockholder Equity']
            stockholders_equity = None
            for key in equity_keys:
                if key in balance_sheet.index:
                    stockholders_equity = balance_sheet.loc[key, latest_year]
                    break
            
            # === 安全性指標用データ ===
            # 流動資産（Current Assets）
            current_assets_keys = ['Current Assets']
            current_assets = None
            for key in current_assets_keys:
                if key in balance_sheet.index:
                    current_assets = balance_sheet.loc[key, latest_year]
                    break
            
            # 流動負債（Current Liabilities）
            current_liabilities_keys = ['Current Liabilities']
            current_liabilities = None
            for key in current_liabilities_keys:
                if key in balance_sheet.index:
                    current_liabilities = balance_sheet.loc[key, latest_year]
                    break
            
            # 固定資産（Non Current Assets）
            non_current_assets_keys = ['Total Non Current Assets', 'Non Current Assets']
            non_current_assets = None
            for key in non_current_assets_keys:
                if key in balance_sheet.index:
                    non_current_assets = balance_sheet.loc[key, latest_year]
                    break
            
            # === キャッシュフローデータ取得 ===
            operating_cf = None
            investing_cf = None
            financing_cf = None
            
            if not cash_flow.empty:
                # 営業キャッシュフロー
                operating_cf_keys = ['Operating Cash Flow', 'Cash Flow From Operating Activities']
                for key in operating_cf_keys:
                    if key in cash_flow.index:
                        operating_cf = cash_flow.loc[key, latest_year]
                        break
                
                # 投資キャッシュフロー
                investing_cf_keys = ['Investing Cash Flow', 'Cash Flow From Investing Activities']
                for key in investing_cf_keys:
                    if key in cash_flow.index:
                        investing_cf = cash_flow.loc[key, latest_year]
                        break
                
                # 財務キャッシュフロー
                financing_cf_keys = ['Financing Cash Flow', 'Cash Flow From Financing Activities']
                for key in financing_cf_keys:
                    if key in cash_flow.index:
                        financing_cf = cash_flow.loc[key, latest_year]
                        break
            
            # === 収益性指標計算 ===
            operating_margin = None
            roe = None
            roa = None
            
            if revenue and operating_income:
                operating_margin = (operating_income / revenue) * 100
            
            if net_income and stockholders_equity:
                roe = (net_income / stockholders_equity) * 100
            
            if net_income and total_assets:
                roa = (net_income / total_assets) * 100
            
            # === 安全性指標計算 ===
            equity_ratio = None
            current_ratio = None
            fixed_ratio = None
            
            if stockholders_equity and total_assets:
                equity_ratio = (stockholders_equity / total_assets) * 100
            
            if current_assets and current_liabilities:
                current_ratio = (current_assets / current_liabilities) * 100
            
            if non_current_assets and stockholders_equity:
                fixed_ratio = (non_current_assets / stockholders_equity) * 100
            
            # === 成長性指標計算 ===
            revenue_growth = None
            operating_income_growth = None
            
            if revenue and prev_revenue and prev_revenue != 0:
                revenue_growth = ((revenue - prev_revenue) / prev_revenue) * 100
            
            if operating_income and prev_operating_income and prev_operating_income != 0:
                operating_income_growth = ((operating_income - prev_operating_income) / prev_operating_income) * 100
            
            # === フリーキャッシュフロー計算 ===
            free_cf = None
            if operating_cf is not None and investing_cf is not None:
                free_cf = operating_cf + investing_cf  # 投資CFは通常負の値

            return {
                'operating_margin': operating_margin,
                'roe': roe,
                'roa': roa,
                'equity_ratio': equity_ratio,
                'current_ratio': current_ratio,
                'fixed_ratio': fixed_ratio,
                'revenue_growth': revenue_growth,
                'operating_income_growth': operating_income_growth,
                'eps': eps,
                'operating_cf': operating_cf / 1e8 if operating_cf else None,  # 億円単位に変換
                'investing_cf': investing_cf / 1e8 if investing_cf else None,  # 億円単位に変換
                'financing_cf': financing_cf / 1e8 if financing_cf else None,  # 億円単位に変換
                'free_cf': free_cf / 1e8 if free_cf else None,  # 億円単位に変換
                'data_source': 'Yahoo Finance参照',
                'year': latest_year.strftime('%Y')
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    @render.text
    def data_source_info():
        """データソース情報を表示"""
        data = financial_data()
        if not data:
            return ""
        if 'error' in data:
            return ""
        return f"データソース: {data.get('data_source', 'データなし')}"

    # === 収益性指標のレンダー関数 ===
    @render.text
    def operating_margin():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['operating_margin'] is not None:
            return f"{data['operating_margin']:.2f}%"
        return "データなし"

    @render.text
    def roe():
        data = financial_data()
        if not data:
            return ui.span("データを取得中...")
        if 'error' in data:
            return ui.span("取得エラー")
        if data['roe'] is not None:
            roe_text = f"{data['roe']:.2f}%"
            return ui.span(roe_text)
        return ui.span("データなし")

    @render.ui
    def roa():
        data = financial_data()
        if not data:
            return ui.span("データを取得中...")
        if 'error' in data:
            return ui.span("取得エラー")
        if data['roa'] is not None:
            roa_text = f"{data['roa']:.2f}%"
            return ui.span(roa_text)
        return ui.span("データなし")
    
    # === 安全性指標のレンダー関数 ===
    @render.ui
    def equity_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['equity_ratio'] is not None:
            ratio = data['equity_ratio']
            # 色と評価テキストを決定
            if ratio >= 50:
                color = "green"
                status = "安全"
            elif ratio >= 20:
                color = "#FFA500"  # オレンジ/黄色
                status = "安定"
            else:
                color = "red"
                status = "要注意"
            
            return ui.span(
                ui.span(f"{ratio:.2f}%", style=f"color: {color}; font-weight: bold;"),
                " ",
                ui.span(f"({status})", style=f"color: {color}; font-weight: bold;")
            )
        return "データなし"

    @render.ui
    def current_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['current_ratio'] is not None:
            ratio = data['current_ratio']
            # 色と評価テキストを決定
            if ratio >= 200:
                color = "green"
                status = "安全"
            elif ratio >= 100:
                color = "#FFA500"  # オレンジ/黄色
                status = "安定"
            else:
                color = "red"
                status = "要注意"
            
            return ui.span(
                ui.span(f"{ratio:.2f}%", style=f"color: {color}; font-weight: bold;"),
                " ",
                ui.span(f"({status})", style=f"color: {color}; font-weight: bold;")
            )
        return "データなし"

    @render.ui
    def fixed_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['fixed_ratio'] is not None:
            ratio = data['fixed_ratio']
            # 色と評価テキストを決定
            if ratio <= 100:
                color = "green"
                status = "安全"
            elif ratio <= 150:
                color = "#FFA500"  # オレンジ/黄色
                status = "安定(やや注意)"
            else:
                color = "red"
                status = "要注意"
            
            return ui.span(
                ui.span(f"{ratio:.2f}%", style=f"color: {color}; font-weight: bold;"),
                " ",
                ui.span(f"({status})", style=f"color: {color}; font-weight: bold;")
            )
        return "データなし"
    
    # === 成長性指標のレンダー関数 ===
    @render.text
    def revenue_growth():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['revenue_growth'] is not None:
            return f"{data['revenue_growth']:.2f}%"
        return "データなし"

    @render.text
    def operating_income_growth():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['operating_income_growth'] is not None:
            return f"{data['operating_income_growth']:.2f}%"
        return "データなし"

    @render.text
    def eps():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['eps'] is not None:
            return f"{data['eps']:.2f}"
        return "データなし"

    # === キャッシュフロー指標のレンダー関数 ===
    @render.ui
    def operating_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['operating_cf'] is not None and not pd.isna(data['operating_cf']):
            value = data['operating_cf']
            return ui.span(f"{value:.2f}億円")
        return "データなし"

    @render.ui
    def investing_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['investing_cf'] is not None and not pd.isna(data['investing_cf']):
            value = data['investing_cf']
            return ui.span(f"{value:.2f}億円")
        return "データなし"

    @render.ui
    def financing_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['financing_cf'] is not None and not pd.isna(data['financing_cf']):
            value = data['financing_cf']
            return ui.span(f"{value:.2f}億円")
        return "データなし"

    @render.ui
    def free_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['free_cf'] is not None and not pd.isna(data['free_cf']):
            value = data['free_cf']
            return ui.span(f"{value:.2f}億円")
        return "データなし"

    return ui.card(
        ui.card_header(
            ui.div(
                ui.div(
                    ui.h4("財務情報", style="margin: 0; display: inline-block;"),
                    ui.span(" | ", style="margin: 0 10px; color: #666; font-size: 1.5em;"),
                    ui.span(
                        ui.output_text("company_name", inline=True),
                        style="font-weight: bold; font-size: 1.5em;"
                    ),
                    style="display: flex; align-items: center;"
                ),
                ui.div(
                    ui.output_text("data_source_info"),
                    style="font-size: 0.9em; color: #666; margin-top: 5px;"
                )
            )
        ),
        ui.card_body(
            # 2×2 グリッドレイアウト
            ui.div(
                # 上段（1行目）
                ui.div(
                    # 左上: 収益性指標
                    ui.card(
                        ui.card_header(
                            "収益性",
                            style="background-color: #e3f2fd;"
                            ),
                        ui.card_body(
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("売上高営業利益率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["operating_margin"]
                                    ),
                                    "："
                                ),
                                ui.output_text("operating_margin", inline=True),
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("ROE", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["roe"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("roe", inline=True),
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("ROA", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["roa"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("roa", inline=True),
                                style="margin-bottom: 0px;"
                            ),
                        )
                    ),
                    
                    # 右上: 安全性指標
                    ui.card(
                        ui.card_header(
                            "安全性",
                            style="background-color: #e3f2fd;"
                            ),
                        ui.card_body(
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("自己資本比率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["equity_ratio"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("equity_ratio", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("流動比率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["current_ratio"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("current_ratio", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("固定比率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["fixed_ratio"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("fixed_ratio", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 0px;"
                            ),
                        )
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;"
                ),
                
                # 下段（2行目）
                ui.div(
                    # 左下: 成長性指標
                    ui.card(
                        ui.card_header(
                            "成長性",
                            style="background-color: #e3f2fd;"
                            ),
                        ui.card_body(
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("売上高成長率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["revenue_growth"]
                                    ),
                                    "："
                                ),
                                ui.output_text("revenue_growth", inline=True),
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("営業利益成長率", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["operating_income_growth"]
                                    ),
                                    "："
                                ),
                                ui.output_text("operating_income_growth", inline=True),
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong("EPS (1株当たり利益)："),
                                ui.output_text("eps", inline=True),
                                style="margin-bottom: 0px;"
                            ),
                        )
                    ),
                    
                    # 右下: キャッシュフロー指標
                    ui.card(
                        ui.card_header(
                            "キャッシュフロー",
                            style="background-color: #e3f2fd;"
                            ),
                        ui.card_body(
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("営業CF", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["operating_cf"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("operating_cf", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("投資CF", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["investing_cf"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("investing_cf", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("財務CF", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["financing_cf"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("financing_cf", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 8px;"
                            ),
                            ui.div(
                                ui.strong(
                                    ui.tooltip(
                                        ui.span("フリーCF", ui.tags.span("?", style="color: white; background-color: #007bff; border-radius: 50%; width: 16px; height: 16px; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; cursor: help; margin-left: 4px;")),
                                        EXPLANATIONS["free_cf"]
                                    ),
                                    "："
                                ),
                                ui.output_ui("free_cf", inline=True),  # output_text から output_ui に変更
                                style="margin-bottom: 0px;"
                            ),
                        )
                    ),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;"
                )
            )
        )
    )
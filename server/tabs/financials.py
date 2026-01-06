from shiny import reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib_fontja
import pandas as pd

CODE_TO_COMPANY = {
    "7203.T": "トヨタ自動車",
    "7974.T": "任天堂",
    "9984.T": "ソフトバンクG"
}

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
        ticker_obj = ticker()
        if not ticker_obj:
            return None
        
        try:
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
                'operating_cf': operating_cf,
                'investing_cf': investing_cf,
                'financing_cf': financing_cf,
                'free_cf': free_cf,
                'year': latest_year.strftime('%Y')
            }
            
        except Exception as e:
            return {'error': str(e)}

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
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['roe'] is not None:
            return f"{data['roe']:.2f}%"
        return "データなし"

    @render.text
    def roa():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['roa'] is not None:
            return f"{data['roa']:.2f}%"
        return "データなし"
    
    # === 安全性指標のレンダー関数 ===
    @render.text
    def equity_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['equity_ratio'] is not None:
            return f"{data['equity_ratio']:.2f}%"
        return "データなし"

    @render.text
    def current_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['current_ratio'] is not None:
            return f"{data['current_ratio']:.2f}%"
        return "データなし"

    @render.text
    def fixed_ratio():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['fixed_ratio'] is not None:
            return f"{data['fixed_ratio']:.2f}%"
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
    @render.text
    def operating_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['operating_cf'] is not None:
            return f"{data['operating_cf']:,.0f}"
        return "データなし"

    @render.text
    def investing_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['investing_cf'] is not None:
            return f"{data['investing_cf']:,.0f}"
        return "データなし"

    @render.text
    def financing_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['financing_cf'] is not None:
            return f"{data['financing_cf']:,.0f}"
        return "データなし"

    @render.text
    def free_cf():
        data = financial_data()
        if not data:
            return "データを取得中..."
        if 'error' in data:
            return "取得エラー"
        if data['free_cf'] is not None:
            return f"{data['free_cf']:,.0f}"
        return "データなし"

    return ui.card(
        ui.card_header(
            ui.div(
                ui.h4("財務情報"),
                ui.output_text("company_name")
            )
        ),
        ui.card_body(
            # 収益性指標
            ui.h5("収益性"),
            ui.div(
                ui.strong("売上高営業利益率："),
                ui.output_text("operating_margin", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("ROE："),
                ui.output_text("roe", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("ROA："),
                ui.output_text("roa", inline=True),
                style="margin-bottom: 20px;"
            ),
            
            # 安全性指標
            ui.h5("安全性"),
            ui.div(
                ui.strong("自己資本比率："),
                ui.output_text("equity_ratio", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("流動比率："),
                ui.output_text("current_ratio", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("固定比率："),
                ui.output_text("fixed_ratio", inline=True),
                style="margin-bottom: 10px;"
            ),

            # 成長性指標
            ui.h5("成長性"),
            ui.div(
                ui.strong("売上高成長率："),
                ui.output_text("revenue_growth", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("営業利益成長率："),
                ui.output_text("operating_income_growth", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("EPS（1株当たり利益）："),
                ui.output_text("eps", inline=True),
                style="margin-bottom: 20px;"
            ),

            # キャッシュフロー指標
            ui.h5("キャッシュフロー"),
            ui.div(
                ui.strong("営業CF："),
                ui.output_text("operating_cf", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("投資CF："),
                ui.output_text("investing_cf", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("財務CF："),
                ui.output_text("financing_cf", inline=True),
                style="margin-bottom: 10px;"
            ),
            ui.div(
                ui.strong("フリーCF："),
                ui.output_text("free_cf", inline=True),
                style="margin-bottom: 10px;"
            )
        )
    )
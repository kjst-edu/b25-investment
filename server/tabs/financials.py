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
            
            if financials.empty or balance_sheet.empty:
                return None
            
            # 最新年度のデータを取得
            latest_year = financials.columns[0]
            
            # 売上高（Revenue/Total Revenue）
            revenue_keys = ['Total Revenue', 'Revenue']
            revenue = None
            for key in revenue_keys:
                if key in financials.index:
                    revenue = financials.loc[key, latest_year]
                    break
            
            # 営業利益（Operating Income）
            operating_income_keys = ['Operating Income', 'EBIT']
            operating_income = None
            for key in operating_income_keys:
                if key in financials.index:
                    operating_income = financials.loc[key, latest_year]
                    break
            
            # 純利益（Net Income）
            net_income_keys = ['Net Income', 'Net Income Common Stockholders']
            net_income = None
            for key in net_income_keys:
                if key in financials.index:
                    net_income = financials.loc[key, latest_year]
                    break
            
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
            
            # 指標計算
            operating_margin = None
            roe = None
            roa = None
            
            if revenue and operating_income:
                operating_margin = (operating_income / revenue) * 100
            
            if net_income and stockholders_equity:
                roe = (net_income / stockholders_equity) * 100
            
            if net_income and total_assets:
                roa = (net_income / total_assets) * 100
            
            return {
                'operating_margin': operating_margin,
                'roe': roe,
                'roa': roa,
                'year': latest_year.strftime('%Y')
            }
            
        except Exception as e:
            return {'error': str(e)}

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

    return ui.card(
        ui.card_header(
            ui.div(
                ui.h4("財務情報"),
                ui.output_text("company_name")
            )
        ),
        ui.card_body(
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
                style="margin-bottom: 10px;"
            )
        )
    )
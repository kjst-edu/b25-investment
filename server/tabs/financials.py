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
        code = input.select_code() if input.select_code() else ""
        company = CODE_TO_COMPANY.get(code, "企業を選択してください")
        return company

    @reactive.calc
    def ticker():
        code = input.select_code()
        if code:
            return yf.Ticker(code)
        return None
    
    # 売上高グラフ
    @render.plot
    def revenue_chart():
        t = ticker()
        if not t:
            return
            
        try:
            financials = t.financials
            
            if financials.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '売上データが取得できませんでした', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                return fig
            
            if 'Total Revenue' in financials.index:
                revenue_data = financials.loc['Total Revenue']
                revenue_data = revenue_data.dropna().sort_index()
                
                if revenue_data.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.text(0.5, 0.5, '売上データがありません', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=16)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    return fig
                
                revenue_oku = revenue_data / 100_000_000
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(range(len(revenue_oku)), revenue_oku.values, 
                             color='steelblue', alpha=0.7)
                
                years = [date.year for date in revenue_oku.index]
                ax.set_xticks(range(len(revenue_oku)))
                ax.set_xticklabels(years, rotation=0)
                
                ax.set_title('売上高推移', fontsize=16, fontweight='bold', pad=20)
                ax.set_ylabel('売上高 (億円)', fontsize=12)
                ax.set_xlabel('年度', fontsize=12)
                
                max_value = max(revenue_oku.values)
                ax.set_ylim(0, max_value * 1.1)
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                
                for bar, value in zip(bars, revenue_oku.values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + max_value*0.01,
                           f'{value:,.0f}', ha='center', va='bottom', fontsize=10)
                
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
    
    # 営業利益グラフ
    @render.plot
    def operating_income_chart():
        t = ticker()
        if not t:
            return
            
        try:
            financials = t.financials
            
            if financials.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '営業利益データが取得できませんでした', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                return fig
            
            if 'Operating Income' in financials.index:
                operating_data = financials.loc['Operating Income']
                operating_data = operating_data.dropna().sort_index()
                
                if operating_data.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.text(0.5, 0.5, '営業利益データがありません', 
                           ha='center', va='center', transform=ax.transAxes, fontsize=16)
                    ax.set_xlim(0, 1)
                    ax.set_ylim(0, 1)
                    ax.axis('off')
                    return fig
                
                operating_oku = operating_data / 100_000_000
                
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(range(len(operating_oku)), operating_oku.values, 
                             color='green', alpha=0.7)
                
                years = [date.year for date in operating_oku.index]
                ax.set_xticks(range(len(operating_oku)))
                ax.set_xticklabels(years, rotation=0)
                
                ax.set_title('営業利益推移', fontsize=16, fontweight='bold', pad=20)
                ax.set_ylabel('営業利益 (億円)', fontsize=12)
                ax.set_xlabel('年度', fontsize=12)
                
                # Y軸の範囲を設定（負の値も考慮）
                min_value = min(operating_oku.values)
                max_value = max(operating_oku.values)
                if min_value < 0:
                    ax.set_ylim(min_value * 1.1, max_value * 1.1)
                    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
                else:
                    ax.set_ylim(0, max_value * 1.1)
                
                ax.grid(axis='y', alpha=0.3, linestyle='--')
                
                for bar, value in zip(bars, operating_oku.values):
                    height = bar.get_height()
                    if height >= 0:
                        ax.text(bar.get_x() + bar.get_width()/2., height + max(max_value*0.01, 0),
                               f'{value:,.0f}', ha='center', va='bottom', fontsize=10)
                    else:
                        ax.text(bar.get_x() + bar.get_width()/2., height - max(abs(min_value)*0.01, 0),
                               f'{value:,.0f}', ha='center', va='top', fontsize=10)
                
                plt.tight_layout()
                return fig
            
            else:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, '営業利益データが見つかりませんでした', 
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
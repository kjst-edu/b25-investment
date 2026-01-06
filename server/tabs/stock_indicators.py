from shiny import reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def ui_content(input, output, session):
    
    @reactive.calc
    def ticker():
        code = input.select_code()
        if code:
            return yf.Ticker(code)
        return None
    
    @reactive.calc
    def stock_data():
        """選択された期間の株価データを取得"""
        ticker_obj = ticker()
        period = input.period() if hasattr(input, 'period') and input.period() else "1y"
        
        if not ticker_obj:
            return None
        
        try:
            # 期間に応じてデータを取得
            hist = ticker_obj.history(period=period)
            if hist.empty:
                return None
            return hist
        except Exception as e:
            return None
    
    @render.plot
    def stock_chart():
        data = stock_data()
        if data is None:
            # データがない場合の空のプロットを作成
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.text(0.5, 0.5, 'データを取得中...', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=ax.transAxes, 
                fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.title("株価チャート")
            return fig
        
        # 株価チャートを作成
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                    gridspec_kw={'height_ratios': [3, 1], 'hspace': 0.5})
        
        # 株価（終値）のプロット
        ax1.plot(data.index, data['Close'], linewidth=2, color='blue', label='終値')
        ax1.set_title(f"株価チャート - {input.select_code()}", fontsize=16, fontweight='bold')
        ax1.set_ylabel("株価 (円)", fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 日付フォーマットの調整
        ax1.tick_params(axis='x', rotation=0)
        
        # 出来高のプロット
        ax2.bar(data.index, data['Volume'], color='orange', alpha=0.7)
        ax2.set_title("出来高", fontsize=14)
        ax2.set_ylabel("出来高", fontsize=12)
        ax2.set_xlabel("日付", fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        return fig
    
    @render.text
    def stock_summary():
        """株価サマリー情報を表示"""
        data = stock_data()
        ticker_obj = ticker()
        
        if data is None or ticker_obj is None:
            return "データを取得中..."
        
        try:
            # 最新の株価情報
            latest_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2] if len(data) > 1 else latest_price
            price_change = latest_price - prev_price
            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            # 期間中の高値・安値
            period_high = data['High'].max()
            period_low = data['Low'].min()
            
            # 平均出来高
            avg_volume = data['Volume'].mean()
            
            summary = f"""現在値: {latest_price:,.0f}円
            前日比: {price_change:+,.0f}円 ({price_change_pct:+.2f}%)
            期間高値: {period_high:,.0f}円
            期間安値: {period_low:,.0f}円
            平均出来高: {avg_volume:,.0f}株"""
            
            return summary
            
        except Exception as e:
            return "データの取得に失敗しました"
    
    return ui.card(
        ui.card_header(
            ui.h4("株価・投資指標")
        ),
        ui.card_body(
            # 株価サマリー（上に移動）
            ui.div(
                ui.h5("株価情報", style="margin-bottom: 8px;"),
                ui.pre(
                    ui.output_text("stock_summary"),
                    style="margin: 0; white-space: pre-line; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;"
                ),
                style="margin-bottom: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff;"
            ),
            
            # 期間選択ボタン
            ui.div(
                ui.h5("表示期間"),
                ui.input_radio_buttons(
                    "period",
                    "",
                    choices={
                        "1mo": "1ヶ月",
                        "3mo": "3ヶ月", 
                        "6mo": "6ヶ月",
                        "1y": "1年",
                        "3y": "3年"
                    },
                    selected="1y",
                    inline=True
                ),
                style="margin-bottom: 5px;"
            ),
            
            # 株価チャート
            ui.div(
                ui.output_plot("stock_chart"),
                style="margin-top: 5px;"
            )
        )
    )
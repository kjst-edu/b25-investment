from shiny import reactive, render, ui
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

current_date = datetime.now().strftime("%Y/%m/%d")

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

            # 前日比の色と符号を決定
            if price_change > 0:
                color = "red"
                sign = "+"
            elif price_change < 0:
                color = "blue"
                sign = ""  # マイナス記号は自動で表示される
            else:
                color = "black"
                sign = ""

            # 投資指標の取得（yfinanceから）
            try:
                info = ticker_obj.info
                per = info.get('forwardPE', info.get('trailingPE', 'N/A'))
                psr = info.get('priceToSalesTrailing12Months', 'N/A')
                pbr = info.get('priceToBook', 'N/A')
                dividend_yield = info.get('dividendYield', 0)
                shares_outstanding = info.get('sharesOutstanding', 'N/A')
                # 日本株の場合、通常は100株単位
                unit_shares = 100  # または info.get('lotSize', 100)
                
                # フォーマット処理
                per_str = f"{per:.1f}" if isinstance(per, (int, float)) and per > 0 else "N/A"
                psr_str = f"{psr:.1f}" if isinstance(psr, (int, float)) and psr > 0 else "N/A"
                pbr_str = f"{pbr:.1f}" if isinstance(pbr, (int, float)) and pbr > 0 else "N/A"
                dividend_str = f"{dividend_yield:.2f}%" if dividend_yield > 0 else "N/A"
                
            except:
                per_str = psr_str = pbr_str = dividend_str = "N/A"
                unit_shares = 100
            
            return ui.div(
                # 左側：株価情報
                ui.div(
                    ui.p(f"現在値： {latest_price:,.0f}円", style="margin: 0; margin-bottom: 8px;"),
                    ui.div(
                        ui.span("前日比： ", style="color: black;"),
                        ui.span(
                            f"{sign}{price_change:,.0f}円 ({sign}{price_change_pct:.2f}%)",
                            style=f"color: {color};"
                        ),
                        style="margin: 0; margin-bottom: 8px;"
                    ),
                    ui.p(f"期間高値： {period_high:,.0f}円", style="margin: 0; margin-bottom: 4px;"),
                    ui.p(f"期間安値： {period_low:,.0f}円", style="margin: 0; margin-bottom: 4px;"),
                    ui.p(f"平均出来高： {avg_volume:,.0f}株", style="margin: 0;"),
                    style="flex: 1; padding-right: 15px;"
                ),
                
                # 右側：投資指標
                ui.div(
                    ui.p(f"単元株数： {unit_shares:,}株", style="margin: 0; margin-bottom: 8px;"),
                    ui.p(f"PER(調整後)： {per_str}倍", style="margin: 0; margin-bottom: 8px;"),
                    ui.p(f"PSR： {psr_str}倍", style="margin: 0; margin-bottom: 4px;"),
                    ui.p(f"PBR： {pbr_str}倍", style="margin: 0; margin-bottom: 4px;"),
                    ui.p(f"配当利回り： {dividend_str}", style="margin: 0;"),
                    style="flex: 1; padding-left: 15px; border-left: 1px solid #ddd;"
                ),
                style="display: flex; align-items: flex-start; font-weight: bold;"
            )
            
        except Exception as e:
            return "データの取得に失敗しました"
    
    # 期間騰落率を表示する新しいレンダー関数を追加
    @render.ui
    def period_return_display():
        """選択期間の騰落率を表示"""
        data = stock_data()
        
        if data is None or len(data) < 2:
            return ""
        
        try:
            latest_price = data['Close'].iloc[-1]
            period_start_price = data['Close'].iloc[0]
            period_return = ((latest_price - period_start_price) / period_start_price * 100) if period_start_price != 0 else 0
            
            color = "red" if period_return >= 0 else "blue"
            sign = "+" if period_return >= 0 else ""
            
            # 期間の日本語表示
            period_labels = {
                "1mo": "1ヶ月",
                "3mo": "3ヶ月",
                "6mo": "6ヶ月",
                "1y": "1年",
                "3y": "3年"
            }
            period = input.period()
            period_label = period_labels.get(period, period)
            
            return ui.span(
                f"({period_label}騰落率: {sign}{period_return:.2f}%)",
                style=f"color: {color}; font-weight: bold; margin-left: 10px;"
            )
            
        except Exception:
            return ""
    
    return ui.card(
        ui.card_header(
            ui.div(
                ui.div(
                    ui.h4("株価・投資指標", style="margin: 0; display: inline-block;"),
                    ui.span(" | ", style="margin: 0 10px; color: #666; font-size: 1.5em;"),
                    ui.span(
                        ui.output_text("company_name", inline=True),
                        style="font-weight: bold; font-size: 1.5em;"
                    ),
                    style="display: flex; align-items: center;"
                )
            )
        ),
        ui.card_body( 
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
            # 株価サマリー（上に移動）
            ui.div(
                ui.div(
                    ui.h5(
                        ui.span(f"株価情報（{current_date} 時点）", style="display: inline;"),
                        ui.output_ui("period_return_display", inline=True),
                        style="margin-bottom: 8px;"
                    ),
                ),
                ui.div(
                    ui.output_ui("stock_summary"),
                    style="margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;"
                ),
                style="margin-bottom: 15px; padding: 12px; background-color: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff;"
            ),
            # 株価チャート
            ui.div(
                ui.output_plot("stock_chart"),
                style="margin-top: 5px;"
            )
        )
    )
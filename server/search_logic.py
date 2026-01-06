from shiny import reactive, render, ui
import pandas as pd
from server.tabs import company_overview, financials, stock_indicators

def load_company_data():
    """master_financial_indicators.csvから証券コードと企業名の辞書を作成"""
    try:
        # CSVファイルを読み込み
        df = pd.read_csv('master_financial_indicators.csv', encoding='utf-8')
        print(f"CSVファイル読み込み完了。総行数: {len(df)}")
        
        # 証券コードと企業名の列を確認
        print(f"列名: {df.columns.tolist()}")
        
        # 欠損値を除外
        df = df.dropna(subset=['証券コード', '企業名'])
        print(f"欠損値除外後の行数: {len(df)}")
        
        # 証券コードと企業名の組み合わせを抽出（重複を除去）
        company_data = df[['証券コード', '企業名']].drop_duplicates()
        print(f"重複除去後のユニークな企業数: {len(company_data)}")
        
        # 証券コードに.Tを追加（yfinance用）
        code_to_company = {}
        for _, row in company_data.iterrows():
            # 証券コードを文字列として処理し、4桁に統一
            code = str(int(float(row['証券コード']))).zfill(4) + '.T'
            company = str(row['企業名']).strip()
            
            # 空の企業名や無効なコードをスキップ
            if company and company != 'nan' and len(code) == 6:  # 4桁+.T
                code_to_company[code] = company
        
        print(f"最終的に作成された辞書のサイズ: {len(code_to_company)}")
        print(f"最初の10社: {dict(list(code_to_company.items())[:10])}")
        
        return code_to_company
        
    except FileNotFoundError:
        print("master_financial_indicators.csv が見つかりません")
        # フォールバック用のデータ
        return {
            "7203.T": "トヨタ自動車",
            "7974.T": "任天堂", 
            "9984.T": "ソフトバンクG"
        }
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        # フォールバック用のデータ
        return {
            "7203.T": "トヨタ自動車",
            "7974.T": "任天堂",
            "9984.T": "ソフトバンクG"
        }

# CSVから辞書を生成
CODE_TO_COMPANY = load_company_data()
COMPANY_TO_CODE = {v: k for k, v in CODE_TO_COMPANY.items()}  # 逆引き辞書

def search_logic(input, output, session):
    active_tab = reactive.value("home")
    selected_code = reactive.value('') # 選択された証券コードを管理

    # 選択ボックスの動的生成
    @render.ui
    def select_code_ui():
        # 証券コードをソートして表示
        sorted_codes = sorted(CODE_TO_COMPANY.keys())
        return ui.input_selectize(
            "select_code", 
            "証券コード", 
            choices=sorted_codes,
            selected=selected_code(),
            options={"placeholder": "証券コードを選択してください"}
        )
    
    @render.ui
    def select_company_ui():
        code = selected_code()
        company = CODE_TO_COMPANY.get(code, "")
        # 企業名をソートして表示
        sorted_companies = sorted(CODE_TO_COMPANY.values())
        return ui.input_selectize(
            "select_company",
            "企業名",
            choices=sorted_companies,
            selected=company,
            options={"placeholder": "企業名を選択してください"}
        )
    
    # データ統計情報を表示（デバッグ用）
    @render.text
    def data_info():
        return f"読み込まれた企業数: {len(CODE_TO_COMPANY)}"
    
    # 証券コードが変更されたときの処理
    @reactive.effect
    @reactive.event(input.select_code)
    def _():
        if input.select_code():
            selected_code.set(input.select_code())
    
    # 企業名が変更されたときの処理
    @reactive.effect
    @reactive.event(input.select_company)
    def _():
        if input.select_company():
            code = COMPANY_TO_CODE.get(input.select_company())
            if code and code != selected_code():
                selected_code.set(code)

    @reactive.effect
    @reactive.event(input.btn1)
    def _():
        active_tab.set("企業概要")
       
    @reactive.effect
    @reactive.event(input.btn2)
    def _():
        active_tab.set("財務情報")
    
    @reactive.effect
    @reactive.event(input.btn3)
    def _():
        active_tab.set("株価・投資指標")

    @render.ui
    def main_tab_content():
        current_tab = active_tab()
        if current_tab == "企業概要":
            return company_overview.ui_content(input, output, session)
        elif current_tab == "財務情報":
            return financials.ui_content(input, output, session)
        elif current_tab == "株価・投資指標":
            return stock_indicators.ui_content(input, output, session)
        else:
            return company_overview.ui_content(input, output, session)
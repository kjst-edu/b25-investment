import pandas as pd

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
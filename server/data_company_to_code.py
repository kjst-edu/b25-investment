import pandas as pd

def load_company_data():
    """company_list_2702.csvから証券コードと企業名の辞書を作成"""
    try:
        # CSVファイルを読み込み
        df = pd.read_csv('company_list_2702.csv', encoding='utf-8')
        print(f"CSVファイル読み込み完了。総行数: {len(df)}")
        
        # 証券コードと企業名の列を確認
        print(f"列名: {df.columns.tolist()}")
        
        # 欠損値を除外
        df = df.dropna(subset=['証券コード', '企業名'])
        print(f"欠損値除外後の行数: {len(df)}")
        
        # 証券コードと企業名、業界の組み合わせを抽出（重複を除去）
        company_data = df[['証券コード', '企業名', '17業種区分']].drop_duplicates()
        print(f"重複除去後のユニークな企業数: {len(company_data)}")
        
        # 各種辞書を作成
        code_to_company = {}
        code_to_industry = {}
        industry_to_codes = {}
        
        for _, row in company_data.iterrows():
            # 証券コードを文字列として処理し、4桁に統一
            code = str(int(float(row['証券コード']))).zfill(4) + '.T'
            company = str(row['企業名']).strip()
            industry = str(row['17業種区分']).strip() if pd.notna(row['17業種区分']) else "その他"
            
            # 空の企業名や無効なコードをスキップ
            if company and company != 'nan' and len(code) == 6:  # 4桁+.T
                code_to_company[code] = company
                code_to_industry[code] = industry
                
                # 業界別のコードリストを作成
                if industry not in industry_to_codes:
                    industry_to_codes[industry] = []
                industry_to_codes[industry].append(code)
        
        print(f"最終的に作成された辞書のサイズ: {len(code_to_company)}")
        print(f"業界数: {len(industry_to_codes)}")
        print(f"業界一覧: {list(industry_to_codes.keys())}")
        
        return code_to_company, code_to_industry, industry_to_codes
        
    except FileNotFoundError:
        print("company_list_2702.csv が見つかりません")
        # フォールバック用のデータ
        fallback_code_to_company = {
            "7203.T": "トヨタ自動車",
            "7974.T": "任天堂", 
            "9984.T": "ソフトバンクグループ"
        }
        fallback_code_to_industry = {
            "7203.T": "輸送用機器",
            "7974.T": "その他製品",
            "9984.T": "情報・通信業"
        }
        fallback_industry_to_codes = {
            "輸送用機器": ["7203.T"],
            "その他製品": ["7974.T"],
            "情報・通信業": ["9984.T"]
        }
        return fallback_code_to_company, fallback_code_to_industry, fallback_industry_to_codes
    except Exception as e:
        print(f"CSVファイルの読み込みエラー: {e}")
        # フォールバック用のデータ
        fallback_code_to_company = {
            "7203.T": "トヨタ自動車",
            "7974.T": "任天堂",
            "9984.T": "ソフトバンクグループ"
        }
        fallback_code_to_industry = {
            "7203.T": "輸送用機器",
            "7974.T": "その他製品",
            "9984.T": "情報・通信業"
        }
        fallback_industry_to_codes = {
            "輸送用機器": ["7203.T"],
            "その他製品": ["7974.T"],
            "情報・通信業": ["9984.T"]
        }
        return fallback_code_to_company, fallback_code_to_industry, fallback_industry_to_codes


# CSVから各種辞書を生成
CODE_TO_COMPANY, CODE_TO_INDUSTRY, INDUSTRY_TO_CODES = load_company_data()
COMPANY_TO_CODE = {v: k for k, v in CODE_TO_COMPANY.items()}  # 逆引き辞書
# extract_financials.py
import pandas as pd

# CSVを読み込む
df_codes = pd.read_csv("edinet_companies_test.csv")
df_codes = df_codes.head(10)  # 10社だけテスト用に抽出

# 財務データリスト（テスト用）
financial_list = []

for index, row in df_codes.iterrows():
    company_name = row["企業名"]
    edinet_code = row["EDINETコード"]
    
    # テスト用のサンプル値（XBRL解析の代わり）
    revenue = 1000000 + index * 10000
    operating_income = 500000 + index * 5000
    net_income = 300000 + index * 3000
    
    financial_data = {
        "企業名": company_name,
        "EDINETコード": edinet_code,
        "売上高": revenue,
        "営業利益": operating_income,
        "純利益": net_income
    }
    financial_list.append(financial_data)
    
    # VS Codeターミナルに表示
    print(financial_data)

# CSVに保存
df_financial = pd.DataFrame(financial_list)
df_financial.to_csv("financial_data_test.csv", index=False, encoding="utf-8-sig")
print("財務データCSV保存完了！件数:", len(df_financial))

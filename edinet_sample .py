# ファイル名: edinet_sample.py
import requests
import pandas as pd

# ------------------------
# 確実にデータがある平日を指定
# ------------------------
date_str = "2024-11-25"  # 無印良品などのデータがある日

# 取得結果リスト
company_list = []

# ------------------------
# EDINET API取得
# ------------------------
url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents.json?date={date_str}"

try:
    response = requests.get(url)
    data = response.json()

    if "results" in data:
        for doc in data["results"]:
            if doc.get("docTypeCode") == "120":  # 有価証券報告書のみ
                company_list.append({
                    "企業名": doc.get("filerName"),
                    "EDINETコード": doc.get("filerCode"),
                    "提出日": date_str
                })
    else:
        print(f"{date_str} のデータはありません")
except Exception as e:
    print(f"取得エラー: {e}")

# ------------------------
# 取得件数を10件に制限（軽量テスト用）
# ------------------------
company_list = company_list[:10]

# CSVに保存
if company_list:
    df = pd.DataFrame(company_list)
    df.to_csv("edinet_companies_test.csv", index=False, encoding="utf-8-sig")
    print("取得件数:", len(df))
    print(df)
else:
    print("取得できたデータはありませんでした。")

# ------------------------
# CSVを読み込んで確認表示
# ------------------------
try:
    df_check = pd.read_csv("edinet_companies_test.csv")
    print("\nCSV確認用表示:")
    print(df_check)
except FileNotFoundError:
    print("CSVファイルが存在しません。")

# get_edinet_codes.py
import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# テスト用に1週間だけ取得
start_date = datetime(2025, 1, 1)
end_date   = datetime(2025, 1, 7)

company_list = []

current = start_date
while current <= end_date:
    date_str = current.strftime("%Y-%m-%d")
    url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents.json?date={date_str}"
    
    try:
        response = requests.get(url)
        data = response.json()
        for doc in data["results"]:
            if doc["docTypeCode"] == "120":  # 有価証券報告書のみ
                company_list.append({
                    "企業名": doc["filerName"],
                    "EDINETコード": doc["filerCode"],
                    "提出日": date_str
                })
    except Exception as e:
        print(f"取得エラー: {date_str} - {e}")
    
    time.sleep(1)
    current += timedelta(days=1)

# CSVに保存
df = pd.DataFrame(company_list)
df.to_csv("edinet_companies_test.csv", index=False, encoding="utf-8-sig")
print("企業リストCSV保存完了！取得件数:", len(df))

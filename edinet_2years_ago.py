from datetime import date, timedelta
import requests
import csv
import time
import json

API_KEY = "9f97057a9e4a41da866258eaee102b8"  # 空白を削除
API_KEY = ""  # 前後の空白なし

BASE_URL = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
TYPE = "2"  # 提出書類＋メタデータ

today = date.today()
start_date = today.replace(year=today.year - 2)
end_date = today.replace(year=today.year - 1)

csv_filename = "edinet_documents_2years_ago.csv"
csv_header = ["date", "docID", "edinetCode", "filerName", "docTypeCode",
              "submitDateTime", "docDescription"]

with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_header)

    current_date = start_date

    while current_date <= end_date:
        params = {
            "date": current_date.strftime("%Y-%m-%d"),
            "type": TYPE,
            "Subscription-Key": API_KEY   # ← ここが正しい
        }

        print(f"--- {current_date} ---")

        try:
            response = requests.get(BASE_URL, params=params)
        except Exception as e:
            print("通信エラー:", e)
            current_date += timedelta(days=1)
            continue

        print("status:", response.status_code)

        if response.status_code != 200:
            print(f"失敗 ({response.status_code})")
            current_date += timedelta(days=1)
            continue

        try:
            data = response.json()
        except json.JSONDecodeError:
            print("JSONエラースキップ")
            current_date += timedelta(days=1)
            continue

        results = data.get("results", [])

        for r in results:
            writer.writerow([
                current_date.strftime("%Y-%m-%d"),
                r.get("docID", ""),
                r.get("edinetCode", ""),
                r.get("filerName", ""),
                r.get("docTypeCode", ""),
                r.get("submitDateTime", ""),
                r.get("docDescription", "")
            ])

        print(f"件数: {len(results)}\n")

        time.sleep(1)
        current_date += timedelta(days=1)

print("完了:", csv_filename)

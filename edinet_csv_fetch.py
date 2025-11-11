import os
import requests
import csv
from datetime import date, timedelta
import time

# === 環境変数からAPIキーを取得 ===
API_KEY = "9f97057a9e4a41da886258eaee102b8"
if not API_KEY:
    raise ValueError("環境変数 'EDINET' が設定されていません。")

# === 設定 ===
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
TYPE = "2"  # 1: メタデータのみ, 2: 提出書類一覧＋メタデータ

# === 期間設定（過去1年） ===
end_date = date.today()
start_date = end_date.replace(year=end_date.year - 1)

# === CSVファイル名とヘッダー ===
csv_filename = "edinet_documents_1year.csv"
csv_header = ["date", "docID", "edinetCode", "filerName", "docTypeCode", "submitDateTime", "docDescription"]

# === CSVファイル作成 ===
with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_header)

    current_date = start_date
    while current_date <= end_date:
        params = {
            "date": current_date.strftime("%Y-%m-%d"),
            "type": TYPE
        }
        headers = {
            "X-API-KEY": API_KEY,
            "User-Agent": "EDINET-API-Example"
        }

        response = requests.get(BASE_URL, params=params, headers=headers)

        # デバッグ用
        print(response.url)
        print(response.status_code)

        if response.status_code == 200:
            data = response.json()
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
            print(f"{current_date} 完了（{len(results)}件）")
        else:
            print(f"{current_date} 失敗: {response.status_code}")

        # API制限対策（1秒休憩）
        time.sleep(1)
        current_date += timedelta(days=1)

print(" 1年分のEDINET書類一覧データをCSVに保存しました")

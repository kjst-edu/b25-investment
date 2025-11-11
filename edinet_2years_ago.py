from datetime import date, timedelta
import requests
import csv
import time

# === APIキー ===
API_KEY = "9f97057a9e4a41da866258eaee102b8"  # 空白を削除
if not API_KEY:
    raise ValueError("環境変数 'EDINET' が設定されていません。")

# === 設定 ===
BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
TYPE = "2"  # 1: メタデータのみ, 2: 提出書類一覧＋メタデータ

# === 期間設定（2年前の1年間） ===
today = date.today()
end_date = today.replace(year=today.year - 1)      # 昨年末まで
start_date = today.replace(year=today.year - 2)    # 2年前の今日から

# === CSVファイル名とヘッダー ===
csv_filename = "edinet_documents_2years_ago.csv"
csv_header = ["date", "docID", "edinetCode", "filerName", "docTypeCode", "submitDateTime", "docDescription"]

# === CSV作成 ===
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
        print(response.url, response.status_code)

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

print("2年前の1年間のEDINET書類一覧データをCSVに保存しました")

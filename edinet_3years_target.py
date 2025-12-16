from datetime import date, timedelta
import requests
import csv
import time
import json
import os

# =========================================
# 設定
# =========================================
API_KEY = "980bb7b3286b48d5b8e171adc05c71ae"

BASE_URL = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
TYPE = "2"  # 提出書類＋メタデータ

# 会社コードで絞る（必要なければ [] にする）
TARGET_EDINET_CODES = ["E02144", "E02142", "E01777"]

# =========================================
# 期間（過去3年）
# =========================================
today = date.today()
start_date = today.replace(year=today.year - 3)
end_date = today

# =========================================
# 出力設定
# =========================================
OUTPUT_DIR = "./edinet_target_3years"
CSV_FILENAME = "edinet_yuho_3years.csv"
csv_path = os.path.join(OUTPUT_DIR, CSV_FILENAME)

CSV_HEADER = [
    "date",
    "docID",
    "edinetCode",
    "filerName",
    "docTypeCode",
    "submitDateTime",
    "docDescription"
]

# =========================================
# フォルダ作成
# =========================================
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"保存先フォルダ: {OUTPUT_DIR}")
print(f"出力ファイル: {csv_path}")

# =========================================
# メイン処理
# =========================================
with open(csv_path, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(CSV_HEADER)

    current_date = start_date

    while current_date <= end_date:
        params = {
            "date": current_date.strftime("%Y-%m-%d"),
            "type": TYPE
        }

        headers = {
            "Subscription-Key": API_KEY
        }

        print(f"取得中: {current_date}")

        try:
            response = requests.get(BASE_URL, params=params, headers=headers)
        except Exception as e:
            print(f"通信エラー: {e}")
            current_date += timedelta(days=1)
            continue

        print("status:", response.status_code)

        if response.status_code != 200:
            print("取得失敗")
            current_date += timedelta(days=1)
            time.sleep(1)
            continue

        try:
            data = response.json()
        except json.JSONDecodeError:
            print("JSONデコードエラー")
            current_date += timedelta(days=1)
            continue

        results = data.get("results", [])
        rows_written = 0

        for r in results:
            edinet_code = r.get("edinetCode", "")
            doc_description = r.get("docDescription", "")

            # ① EDINETコードでフィルタ
            if TARGET_EDINET_CODES:
                if edinet_code not in TARGET_EDINET_CODES:
                    continue

            # ② 有価証券報告書のみ抽出（★重要）
            if "有価証券報告書" not in doc_description:
                continue

            writer.writerow([
                current_date.strftime("%Y-%m-%d"),
                r.get("docID", ""),
                edinet_code,
                r.get("filerName", ""),
                r.get("docTypeCode", ""),
                r.get("submitDateTime", ""),
                doc_description
            ])

            rows_written += 1

        print(f"{current_date} -> 保存件数: {rows_written} / 全体: {len(results)}\n")

        time.sleep(1)
        current_date += timedelta(days=1)

print("完了しました")
print(f"CSVファイル: {csv_path}")

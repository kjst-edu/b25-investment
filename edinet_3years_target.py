from datetime import date, timedelta
import requests
import csv
import time
import json
import os 

# === 設定をここに記述 ===
# ⚠️ 注意: 実際のAPIキーを設定してください
API_KEY = "980bb7b3286b48d5b8e171adc05c71ae" 

BASE_URL = "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json"
TYPE = "2"  # 提出書類＋メタデータ
# 🎯 絞り込みたい書類タイプコード (空のリストにすると全て取得)
TARGET_DOC_TYPES = ["S100TR7I", "S100TXFX","S100TS7P"] # 例: 120(有価証券報告書), 140(四半期報告書)

# === 期間設定（過去3年間）===
today = date.today()
start_date = today.replace(year=today.year - 3)
end_date = today

# === ファイルとフォルダのパス設定 ===
OUTPUT_DIR = "./edinet_data_list" # 新しく作成する保存フォルダ
RAW_CSV_FILENAME = "edinet_documents_3years.csv"
csv_filename = os.path.join(OUTPUT_DIR, RAW_CSV_FILENAME) # フォルダとファイル名を結合

csv_header = ["date", "docID", "edinetCode", "filerName", "docTypeCode",
              "submitDateTime", "docDescription"]

# フォルダが存在しない場合は作成
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"データ保存先フォルダ: {OUTPUT_DIR} を確認しました。")

# === メインループ ===
print(f"処理期間: {start_date} から {end_date} までの書類一覧を取得します。")

with open(csv_filename, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(csv_header)

    current_date = start_date

    while current_date <= end_date:
        params = {
            "date": current_date.strftime("%Y-%m-%d"),
            "type": TYPE,
            "Subscription-Key": API_KEY
        }

        try:
            response = requests.get(BASE_URL, params=params)
        except Exception as e:
            print("通信エラー:", e)
            current_date += timedelta(days=1)
            continue

        if response.status_code != 200:
            print(f"{current_date} 失敗 ({response.status_code})。5秒待機します。")
            time.sleep(5) 
            current_date += timedelta(days=1)
            continue

        try:
            data = response.json()
        except json.JSONDecodeError:
            print("JSONエラースキップ")
            current_date += timedelta(days=1)
            continue

        results = data.get("results", [])
        rows_written = 0

        for r in results:
            doc_type = r.get("docTypeCode", "")
            
            # 書類タイプフィルタリング処理
            if TARGET_DOC_TYPES and doc_type not in TARGET_DOC_TYPES:
                continue

            writer.writerow([
                current_date.strftime("%Y-%m-%d"),
                r.get("docID", ""),
                r.get("edinetCode", ""),
                r.get("filerName", ""),
                r.get("docTypeCode", ""),
                r.get("submitDateTime", ""),
                r.get("docDescription", "")
            ])
            rows_written += 1

        print(f"{current_date} 完了。件数: {rows_written} (全{len(results)}件からフィルタリング)")

        time.sleep(1)
        current_date += timedelta(days=1)

print(f"完了しました。書類一覧データは {csv_filename} に保存されました。")
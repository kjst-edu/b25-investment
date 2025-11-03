import requests
import zipfile
import io
import os
import pandas as pd

# === 1. 保存フォルダを作る ===
output_dir = "edinet_data"
os.makedirs(output_dir, exist_ok=True)

# === 2. 取得する日付を設定 ===
# 例：2024年3月31日提出分を取得
date = "2024-03-31"

# === 3. EDINET APIから日付指定でリストを取得 ===
url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents.json?date={date}"
response = requests.get(url)
data = response.json()

# === 4. 特定企業の有価証券報告書だけ抽出 ===
# ここでは一例として「ソニーグループ」を探す
target_docs = [
    d for d in data["results"]
    if "有価証券報告書" in d["docDescription"] and "ソニー" in (d["filerName"] or "")
]

print(f"該当企業数: {len(target_docs)}")

# === 5. 1社だけダウンロードして展開 ===
if target_docs:
    doc_id = target_docs[0]["docID"]
    download_url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{doc_id}?type=1"

    print(f"ダウンロード中: {target_docs[0]['filerName']}")
    res = requests.get(download_url)

    # zipを展開
    with zipfile.ZipFile(io.BytesIO(res.content)) as z:
        z.extractall(output_dir)

    print("ダウンロード完了。展開フォルダ:", output_dir)
else:
    print("該当する書類が見つかりませんでした。")

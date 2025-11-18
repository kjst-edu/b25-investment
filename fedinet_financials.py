import os
import requests
import zipfile
from lxml import etree
import csv

# === 設定 ===
API_KEY = os.environ.get("EDINET")  # 環境変数に EDINET API キー
docIDs = ["XXXXXXXXX", "YYYYYYYYY"]  # ここに取得済みの docID を複数入れる
output_csv = "financial_data.csv"

# 指標タグの候補辞書
TAG_MAPPING = {
    "売上高": ["SalesRevenue", "Revenue", "NetSalesRevenue"],
    "当期純利益": ["NetIncome", "ProfitLoss"],
    "総資産": ["Assets", "TotalAssets"]
}

# CSV ヘッダー
header = ["docID"] + list(TAG_MAPPING.keys())

# CSV 作成
with open(output_csv, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)

    for docID in docIDs:
        print(f"処理中: {docID}")
        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{docID}"
        params = {"type": 1}  # XBRL
        headers = {
            "X-API-KEY": API_KEY,
            "User-Agent": "EDINET-API-Example"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"{docID} 取得失敗: {response.status_code}")
            continue

        # zip 保存して解析
        zip_path = f"{docID}.zip"
        with open(zip_path, "wb") as f:
            f.write(response.content)

        with zipfile.ZipFile(zip_path, 'r') as z:
            xbrl_file = None
            for filename in z.namelist():
                if filename.endswith(".xbrl"):
                    xbrl_file = filename
                    break
            if not xbrl_file:
                print(f"{docID} XBRL ファイルなし")
                continue

            with z.open(xbrl_file) as f:
                tree = etree.parse(f)
                root = tree.getroot()
                nsmap = root.nsmap
                jpfr_ns = nsmap.get("jpfr-di", "")  # 名前空間取得

                row = [docID]
                for key, candidates in TAG_MAPPING.items():
                    value = None
                    for tag in candidates:
                        el = root.find(f".//{{{jpfr_ns}}}{tag}")
                        if el is not None and el.text:
                            value = el.text
                            break
                    row.append(value if value is not None else "N/A")

                writer.writerow(row)

        # zip を削除して軽くする
        os.remove(zip_path)

print(f"CSV 保存完了: {output_csv}")

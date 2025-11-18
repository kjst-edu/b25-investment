import os
import requests
import zipfile
from lxml import etree
import csv

# ===== 設定 =====
API_KEY = "e675a431de2a412681794f62c8850a20"  # EDINETのSubscription-Key
DOC_IDS = ["S100TR7I", "S100SR8E"]  # 取得したい書類のdocIDをリストで指定
OUTPUT_CSV = "financial_data.csv"
SAVE_DIR = "./downloaded_docs"  # zipファイル一時保存先

os.makedirs(SAVE_DIR, exist_ok=True)

# ===== 指標タグ辞書 =====
TAG_MAPPING = {
    "売上高": ["SalesRevenue", "Revenue", "NetSalesRevenue", "経常収益"],
    "当期純利益": ["NetIncome", "ProfitLoss", "当期純利益"],
    "総資産": ["Assets", "TotalAssets", "総資産"]
}

# CSVヘッダー作成
header = ["docID"] + list(TAG_MAPPING.keys())

with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)

    for docID in DOC_IDS:
        print(f"\n処理中: {docID}")

        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{docID}"
        params = {"type": 1, "Subscription-Key": API_KEY}  # XBRL取得
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"{docID} 取得失敗: {response.status_code}")
            continue

        # zipとして保存
        zip_path = os.path.join(SAVE_DIR, f"{docID}.zip")
        with open(zip_path, "wb") as f:
            f.write(response.content)

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                xbrl_file = None
                for filename in z.namelist():
                    if filename.endswith(".xbrl"):
                        xbrl_file = filename
                        break
                if not xbrl_file:
                    print(f"{docID} XBRLファイルなし")
                    continue

                with z.open(xbrl_file) as f:
                    tree = etree.parse(f)
                    root = tree.getroot()

                    row = [docID]
                    for key, candidates in TAG_MAPPING.items():
                        value = None
                        for tag in candidates:
                            # 名前空間に依存せず検索
                            el = root.find(f".//{{*}}{tag}")
                            if el is not None and el.text:
                                value = el.text
                                break
                        row.append(value if value else "N/A")

                    writer.writerow(row)

        except zipfile.BadZipFile:
            print(f"{docID} はZIPファイルではありません")
        finally:
            os.remove(zip_path)

print(f"\nCSV 保存完了 → {OUTPUT_CSV}")

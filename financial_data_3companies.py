
# %% 3社のみ、15指標を取得する完全版コード
import os
import requests
import zipfile
from lxml import etree
import csv
import time
import pandas as pd

# ===== 設定 =====
API_KEY = ""  # ここにEDINET APIキーを入力
OUTPUT_CSV = "financial_data_3companies.csv"
SAVE_DIR = "./downloaded_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

# ===== 取得対象docID =====
TARGET_DOCS = ["S100TP24","S100SN96","S100UG61"]

# ===== 15指標のタグ候補（できるだけ多く） =====
TAG_CANDIDATES = {
    "売上高": ["NetSales","OperatingRevenue","Revenue","SalesRevenue","SalesRevenueNet","NetOperatingRevenue","営業収益","収益","営業総収入"],
    "営業利益": ["OperatingIncome","OperatingProfit","IncomeFromOperations","営業利益","営業損益"],
    "当期純利益": ["ProfitLoss","NetIncomeLoss","NetIncome","Profit","当期純利益","親会社に帰属する当期純利益","純利益"],
    "総資産": ["Assets","総資産"],
    "自己資本": ["Equity","StockholdersEquity","自己資本","純資産"],
    "流動資産": ["CurrentAssets","流動資産"],
    "流動負債": ["CurrentLiabilities","流動負債"],
    "固定資産": ["NoncurrentAssets","固定資産","非流動資産"],
    "負債総額": ["Liabilities","負債合計","総負債"],
    "営業CF": ["NetCashProvidedByUsedInOperatingActivities","OperatingCashFlow","営業活動によるキャッシュフロー","営業活動CF"],
    "投資CF": ["NetCashProvidedByUsedInInvestingActivities","投資活動によるキャッシュフロー","投資活動CF"],
    "財務CF": ["NetCashProvidedByUsedInFinancingActivities","財務活動によるキャッシュフロー","財務活動CF"],
    "EPS": ["EarningsPerShareBasic","BasicEarningsLossPerShare","1株当たり当期純利益","EPS"],
    "発行株式数": ["NumberOfIssuedAndOutstandingShares","WeightedAverageNumberOfSharesOutstandingBasic","発行株式数","期中平均株式数"],
    "営業CFマージン": []  # 後で計算
}

# ===== CSV 書き込み準備 =====
header = ["docID"] + list(TAG_CANDIDATES.keys())
write_header = not os.path.exists(OUTPUT_CSV)
f = open(OUTPUT_CSV,"a",newline="",encoding="utf-8-sig")
writer = csv.writer(f)
if write_header:
    writer.writerow(header)

# ===== XBRL から数値抽出 =====
def extract_value(root, candidates):
    results = []
    for elem in root.iter():
        tag = etree.QName(elem).localname
        for cand in candidates:
            if cand.lower() in tag.lower():
                val = elem.text
                if val:
                    val = val.replace(",","").replace(" ","")
                    try:
                        results.append(float(val))
                    except:
                        pass
    if results:
        return max(results)
    return None

# ===== 3社分ループ処理 =====
for i, docID in enumerate(TARGET_DOCS, 1):
    print(f"[{i}/{len(TARGET_DOCS)}] 処理中: {docID}")
    try:
        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{docID}"
        params = {"type":1,"Subscription-Key":API_KEY}
        r = requests.get(url, params=params, timeout=30)
        if r.status_code != 200:
            print(f"{docID} 取得失敗: {r.status_code}")
            continue

        zip_path = os.path.join(SAVE_DIR,f"{docID}.zip")
        with open(zip_path,"wb") as zf:
            zf.write(r.content)

        with zipfile.ZipFile(zip_path,"r") as z:
            xbrl_file = next((fn for fn in z.namelist() if fn.endswith(".xbrl")), None)
            if not xbrl_file:
                print(f"{docID} XBRLなし")
                continue

            with z.open(xbrl_file) as xf:
                tree = etree.parse(xf)
                root = tree.getroot()
                row = [docID]
                for key in TAG_CANDIDATES:
                    if key == "営業CFマージン":
                        row.append(None)
                        continue
                    val = extract_value(root, TAG_CANDIDATES[key])
                    row.append(val)
                writer.writerow(row)

        os.remove(zip_path)

    except Exception as e:
        print(f"{docID} エラー: {e}")

    time.sleep(0.5)

f.close()
print(f"\n完了 → {OUTPUT_CSV}")

# %%

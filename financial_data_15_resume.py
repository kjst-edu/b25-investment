import os
import requests
import zipfile
from lxml import etree
import csv
import time
import pandas as pd

# ===== 設定 =====
API_KEY = ""  # EDINET APIキー
DOC_IDS_CSV = "yuho_list.csv"  # 有価証券報告書リスト
OUTPUT_CSV = "financial_data_15_resume.csv"
SAVE_DIR = "./downloaded_docs"
os.makedirs(SAVE_DIR, exist_ok=True)

# ===== 15指標のタグ候補 =====
TAG_CANDIDATES = {
    "売上高": ["jppfs_cor:NetSales","jpigp_cor:NetSales","jpfrta_cor:OperatingRevenue","Revenue","OperatingRevenue"],
    "営業利益": ["jppfs_cor:OperatingIncome","jpigp_cor:OperatingIncome","OperatingIncome"],
    "当期純利益": ["jppfs_cor:ProfitLoss","jpigp_cor:ProfitLoss","NetIncome","us-gaap:NetIncomeLoss"],
    "総資産": ["jppfs_cor:Assets","jpigp_cor:Assets","us-gaap:Assets"],
    "自己資本": ["jppfs_cor:Equity","jpigp_cor:Equity","us-gaap:StockholdersEquity"],
    "流動資産": ["jppfs_cor:CurrentAssets","jpigp_cor:CurrentAssets","us-gaap:AssetsCurrent"],
    "流動負債": ["jppfs_cor:CurrentLiabilities","jpigp_cor:CurrentLiabilities","us-gaap:LiabilitiesCurrent"],
    "固定資産": ["jppfs_cor:NoncurrentAssets","jpigp_cor:NoncurrentAssets","us-gaap:AssetsNoncurrent"],
    "負債総額": ["jppfs_cor:Liabilities","jpigp_cor:Liabilities","us-gaap:Liabilities"],
    "営業CF": ["jppfs_cor:NetCashProvidedByUsedInOperatingActivities","us-gaap:NetCashProvidedByUsedInOperatingActivities","OperatingCashFlow"],
    "投資CF": ["jppfs_cor:NetCashProvidedByUsedInInvestingActivities","us-gaap:NetCashProvidedByUsedInInvestingActivities"],
    "財務CF": ["jppfs_cor:NetCashProvidedByUsedInFinancingActivities","us-gaap:NetCashProvidedByUsedInFinancingActivities"],
    "EPS": ["jppfs_cor:EarningsPerShareBasic","jppfs_cor:BasicEarningsLossPerShare","us-gaap:EarningsPerShareBasic"],
    "発行株式数": ["jppfs_cor:NumberOfIssuedAndOutstandingShares","us-gaap:WeightedAverageNumberOfSharesOutstandingBasic"],
    "営業CFマージン": []  # 後で計算
}

# ===== CSV読み込み、再開対応 =====
if os.path.exists(OUTPUT_CSV):
    existing_df = pd.read_csv(OUTPUT_CSV)
    processed_docIDs = set(existing_df["docID"].tolist())
else:
    existing_df = pd.DataFrame()
    processed_docIDs = set()

df_ids = pd.read_csv(DOC_IDS_CSV)
DOC_IDS = [doc for doc in df_ids["docID"].tolist() if doc not in processed_docIDs]

# ===== 関数 =====
def extract_value(root, candidates):
    results = []
    for elem in root.iter():
        tag = etree.QName(elem).localname
        if tag in [t.split(":")[-1] for t in candidates]:
            val = elem.text
            if val and val.replace(",","").replace(".","").isdigit():
                results.append((tag, float(val.replace(",",""))))
    if results:
        # とりあえず最大値を採用（複数ある場合）
        return max(results, key=lambda x: x[1])[1]
    return None

# ===== CSV準備 =====
header = ["docID"] + list(TAG_CANDIDATES.keys())
write_header = not os.path.exists(OUTPUT_CSV)

with open(OUTPUT_CSV,"a",newline="",encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    if write_header:
        writer.writerow(header)
    
    # ===== docIDごとに処理 =====
    for i, docID in enumerate(DOC_IDS,1):
        print(f"[{i}/{len(DOC_IDS)}] 処理中: {docID}")
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

print(f"\n完了 → {OUTPUT_CSV}")

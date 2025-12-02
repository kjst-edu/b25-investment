#%%
import os
import requests
import zipfile
from lxml import etree
import csv

# ===== 設定 =====
API_KEY = ""  # EDINETのSubscription-Key
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
#%%
#%%
import os
import requests
import zipfile
import csv
# lxmlの代わりに、edinet_xbrlライブラリを使用
from edinet_xbrl.edinet_xbrl_parser import EdinetXbrlParser
from io import BytesIO # zipファイルの内容をメモリで扱うためにインポート

# ===== 設定 =====
API_KEY = "e675a431de2a412681794f62c8850a20"  # EDINETのSubscription-Keyをここに設定
DOC_IDS = ["S100TR7I", "S100SR8E"]  # 取得したい書類のdocIDをリストで指定
OUTPUT_CSV = "financial_data_improved.csv"
SAVE_DIR = "./downloaded_docs_temp" # 一時保存先

os.makedirs(SAVE_DIR, exist_ok=True)

# ===== 指標タグ辞書 (EDINETの主要タクソノミタグ候補を含む) =====
# 記事にあるように、XBRLタグは企業や提出様式によって異なります。
# ここでは、主要なEDINETのタグに加えて、記事の例（OrdinaryIncomeLossSummaryOfBusinessResultsなど）を参考にします。
# コンテキストは「CurrentYearDuration」を優先します。

TAG_MAPPING = {
    "売上高": ["NetSales", "NetSalesSummaryOfBusinessResults", "Revenue", "NetSalesRevenue", "経常収益"],
    "当期純利益": ["ProfitLoss", "NetIncome", "NetIncomeLoss", "当期純利益"],
    "総資産": ["Assets", "TotalAssets", "総資産"],
    "営業利益": ["OperatingIncome", "LossOnOperations"], # 追加でよく使う指標
    "純資産": ["NetAssets", "Equity"] # 追加でよく使う指標
}

# データの取得ロジックを関数化
def get_xbrl_value(edinet_xbrl_object, key_candidates, context_ref="CurrentYearDuration"):
    """
    edinet_xbrlオブジェクトから、指定されたタグ候補とコンテキストのリファレンスで値を取得する。
    """
    for key in key_candidates:
        # EDINET XBRLパーサーの機能を使って、keyとcontext_refを指定してデータを取得
        data = edinet_xbrl_object.get_data_by_context_ref(key, context_ref)
        
        if data is not None and data.get_value() is not None:
            return data.get_value()
    return "N/A"

# CSVヘッダー作成
header = ["docID"] + list(TAG_MAPPING.keys())

with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(header)

    parser = EdinetXbrlParser()
    
    for docID in DOC_IDS:
        print(f"\n処理中: {docID}")

        url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{docID}"
        params = {"type": 1, "Subscription-Key": API_KEY}  # XBRL取得
        
        # 記事の「書類取得API」と同様にリクエスト
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"{docID} 取得失敗: {response.status_code}")
            continue
            
        # zipファイルとしてメモリに読み込む (一時ファイルは作らない)
        try:
            # BytesIOを使ってメモリ上でzipファイルを扱う
            with zipfile.ZipFile(BytesIO(response.content), 'r') as z:
                # PublicDoc/XXX.xbrl ファイルを探す
                xbrl_file_path = None
                for filename in z.namelist():
                    # 記事にもあるように、XBRL/PublicDoc/*.xbrl が目的のファイル
                    if filename.endswith(".xbrl") and "PublicDoc" in filename:
                        xbrl_file_path = filename
                        break
                        
                if not xbrl_file_path:
                    print(f"{docID} XBRLファイルなし")
                    continue

                # EdinetXbrlParserを使ってzip内のXBRLファイルをパース
                # 記事の例: edinet_xbrl_object = parser.parse_file(xbrl_file_path) を参考に、
                # zip内のファイルオブジェクトを直接読み込めるように処理を調整
                with z.open(xbrl_file_path) as f:
                    # zip内のファイルオブジェクトを一時的に保存し、parser.parse_fileで読み込ませる
                    # （edinet_xbrlパーサーはファイルパスを求めるため、一旦テンポラリに保存する）
                    temp_path = os.path.join(SAVE_DIR, f"{docID}_temp_xbrl.xbrl")
                    with open(temp_path, "wb") as temp_f:
                        temp_f.write(f.read())

                    edinet_xbrl_object = parser.parse_file(temp_path)
                    
                    row = [docID]
                    # 主要コンテキスト（最新年度）でデータを取得
                    for key, candidates in TAG_MAPPING.items():
                        # get_xbrl_value関数で値を取得
                        value = get_xbrl_value(edinet_xbrl_object, candidates, 
                                               context_ref='CurrentYearDuration')
                        row.append(value)
                    
                    writer.writerow(row)
                    
                    # テンポラリファイルを削除
                    os.remove(temp_path)

        except zipfile.BadZipFile:
            print(f"{docID} はZIPファイルではありません")
        except Exception as e:
            print(f"{docID} 処理中にエラーが発生しました: {e}")


print(f"\nCSV 保存完了 → {OUTPUT_CSV}")
#%%
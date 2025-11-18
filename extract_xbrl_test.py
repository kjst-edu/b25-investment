import zipfile
import os
import xml.etree.ElementTree as ET

# ===== 設定 =====
DOC_ID = "S100TR7I"
SAVE_DIR = "./edinet_downloads"
ZIP_FILE = os.path.join(SAVE_DIR, f"{DOC_ID}.zip")
EXTRACT_DIR = os.path.join(SAVE_DIR, DOC_ID)  # 解凍先フォルダ

# ===== ZIP解凍 =====
os.makedirs(EXTRACT_DIR, exist_ok=True)
with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
    zip_ref.extractall(EXTRACT_DIR)

print(f"ZIP解凍完了 → {EXTRACT_DIR}")

# ===== XBRLファイル検索 =====
xbrl_file = None
for file in os.listdir(EXTRACT_DIR):
    if file.endswith(".xbrl") or file.endswith(".xml"):
        xbrl_file = os.path.join(EXTRACT_DIR, file)
        break

if not xbrl_file:
    print("XBRLファイルが見つかりません")
    exit()

print(f"XBRLファイル → {xbrl_file}")

# ===== XMLパース =====
tree = ET.parse(xbrl_file)
root = tree.getroot()

# 名前空間を取得
ns = {k if k else 'jp': v for k, v in root.attrib.items() if '}' in k or 'xmlns' in k}

# 値を取得する関数
def get_value(tag):
    for elem in root.findall(f".//{tag}", ns):
        if elem.text and elem.text.strip() != "":
            return elem.text.strip()
    return None

売上高 = get_value("Revenues")        # XBRLのタグに合わせて変更
当期純利益 = get_value("ProfitLoss")  # XBRLのタグに合わせて変更

print("売上高:", 売上高)
print("当期純利益:", 当期純利益)

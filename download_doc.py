import requests
import os

# ===== 設定 =====
API_KEY = ""        # ←ここに実際のAPIキーを入れる
docID = "S100TR7I"                # トヨタ自動車の有価証券報告書
SAVE_DIR = "./edinet_downloads"   # 保存先フォルダ

# ディレクトリ作成
os.makedirs(SAVE_DIR, exist_ok=True)

# ===== ダウンロード =====
url = f"https://disclosure.edinet-fsa.go.jp/api/v2/documents/{docID}"
headers = {"X-API-KEY": API_KEY}

print("Downloading", docID)

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("エラー:", response.status_code, response.text)
    exit()

# ZIPとして保存
zip_filename = os.path.join(SAVE_DIR, f"{docID}.zip")
with open(zip_filename, "wb") as f:
    f.write(response.content)

print(f"ダウンロード完了 → {zip_filename}")
